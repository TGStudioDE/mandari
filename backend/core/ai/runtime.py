from __future__ import annotations

from typing import Dict, List, Optional
from django.utils import timezone
from datetime import timedelta

from ..models import AIAllowedModel, AIProviderConfig, AIUsageLog, Team, AIModelRegistry
from .providers import get_provider


def _select_provider_and_model(team: Team, capability: str) -> tuple[AIProviderConfig, str]:
	allowed = (
		AIAllowedModel.objects.select_related("model", "team")
		.filter(team=team, enabled=True, model__capability=capability)
		.order_by("-model__is_default")
	)
	if not allowed.exists():
		raise ValueError("Kein zulässiges Modell für diese Fähigkeit konfiguriert")
	model_row = allowed.first().model
	prov_cfg = (
		AIProviderConfig.objects.filter(team=team, provider=model_row.provider, enabled=True).first()
	)
	if not prov_cfg:
		raise ValueError("Kein aktiver Provider für das gewählte Modell vorhanden")
	return prov_cfg, model_row.name


def _precheck_limits(cfg: AIProviderConfig, team: Team) -> None:
	"""Einfache Preflight-Prüfungen für EU-Only und Rate-Limits."""
	# EU-only: wenn aktiv und Region nicht EU*, blocken
	if cfg.eu_only and cfg.region and not cfg.region.lower().startswith("eu"):
		raise ValueError("EU-only erzwungen: Region nicht zulässig")
	# RPM/TPM rudimentär prüfen via Logs der letzten 60s
	window_start = timezone.now() - timedelta(seconds=60)
	recent = AIUsageLog.objects.filter(team=team, created_at__gte=window_start)
	if cfg.rpm_limit and recent.count() >= cfg.rpm_limit:
		raise ValueError("Rate Limit (RPM) erreicht")
	if cfg.tpm_limit:
		tokens = 0
		for row in recent.values("prompt_tokens", "completion_tokens"):
			tokens += int(row.get("prompt_tokens") or 0) + int(row.get("completion_tokens") or 0)
		if tokens >= cfg.tpm_limit:
			raise ValueError("Token Limit (TPM) erreicht")
	# Tageslimit Tokens
	if cfg.daily_token_limit:
		from django.db.models.functions import TruncDate
		from django.db.models import Sum
		today = timezone.now().date()
		today_tokens = (
			AIUsageLog.objects.filter(team=team, created_at__date=today)
			.aggregate(total=Sum("prompt_tokens") + Sum("completion_tokens"))
			.get("total")
			or 0
		)
		if today_tokens >= cfg.daily_token_limit:
			raise ValueError("Tages-Tokenlimit erreicht")
	# Monatsbudget (Kosten)
	if cfg.monthly_budget_cents:
		start_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		from django.db.models import Sum
		spent = (
			AIUsageLog.objects.filter(team=team, created_at__gte=start_month)
			.aggregate(total=Sum("cost_cents"))
			.get("total")
			or 0
		)
		if spent >= cfg.monthly_budget_cents:
			raise ValueError("Monatsbudget erreicht")


def _compute_cost_cents(provider: str, model_name: str, prompt_tokens: int, completion_tokens: int) -> int:
	try:
		reg = AIModelRegistry.objects.get(provider=provider, name=model_name)
		cost_prompt = (prompt_tokens * reg.cost_prompt_mtokens) / 1000.0
		cost_completion = (completion_tokens * reg.cost_completion_mtokens) / 1000.0
		return int(round(cost_prompt + cost_completion))
	except AIModelRegistry.DoesNotExist:
		return 0


def _log_usage(team: Team, provider: str, model: str, use_case: str, prompt_tokens: int, completion_tokens: int, request_chars: int, response_chars: int, success: bool, status_code: int, metadata: Optional[Dict] = None, user=None, request_preview: str = "", response_preview: str = "", cost_cents: Optional[int] = None) -> None:
    AIUsageLog.objects.create(
		tenant=team.tenant,
		team=team,
		user=user,
		provider=provider,
		model=model,
		use_case=use_case,
		request_chars=request_chars,
        request_preview=request_preview[:500],
		response_chars=response_chars,
        response_preview=response_preview[:500],
		prompt_tokens=prompt_tokens,
		completion_tokens=completion_tokens,
        cost_cents=0 if cost_cents is None else cost_cents,
		success=success,
		status_code=status_code,
		metadata=metadata or {},
	)


def perform_test_call(config: AIProviderConfig) -> Dict:
	provider = get_provider(config.provider, api_key=config.api_key, base_url=config.base_url)
	resp = provider.generate(model="gpt-3.5-turbo", prompt="Sag 'OK' ohne weitere Worte.", max_tokens=4)
	return {"status": resp.status_code, "text": (resp.text or "")[:200], "error": resp.provider_error}


def summarize(team: Team, text: str, user=None) -> str:
	try:
		cfg, model_name = _select_provider_and_model(team, capability="text")
		_precheck_limits(cfg, team)
		provider = get_provider(cfg.provider, cfg.api_key, cfg.base_url)
		resp = provider.generate(model=model_name, prompt=f"Fasse folgenden Text kurz zusammen:\n\n{text}")
    	cost = _compute_cost_cents(cfg.provider, model_name, resp.usage.get("prompt_tokens", 0), resp.usage.get("completion_tokens", 0))
    	_log_usage(team, cfg.provider, model_name, "summarize", resp.usage.get("prompt_tokens", 0), resp.usage.get("completion_tokens", 0), len(text), len(resp.text or ""), resp.status_code < 400, resp.status_code, user=user, request_preview=text, response_preview=resp.text or "", cost_cents=cost)
		if resp.status_code >= 400 or not resp.text:
			return _fallback_summary(text)
		return resp.text
	except Exception:
		return _fallback_summary(text)


def keywords(team: Team, text: str, user=None) -> List[str]:
	try:
		cfg, model_name = _select_provider_and_model(team, capability="text")
		_precheck_limits(cfg, team)
		provider = get_provider(cfg.provider, cfg.api_key, cfg.base_url)
		resp = provider.generate(model=model_name, prompt=f"Extrahiere 5-10 prägnante Keywords, als Liste, ohne Erklärungen:\n\n{text}")
    	cost = _compute_cost_cents(cfg.provider, model_name, resp.usage.get("prompt_tokens", 0), resp.usage.get("completion_tokens", 0))
    	_log_usage(team, cfg.provider, model_name, "keywords", resp.usage.get("prompt_tokens", 0), resp.usage.get("completion_tokens", 0), len(text), len(resp.text or ""), resp.status_code < 400, resp.status_code, user=user, request_preview=text, response_preview=resp.text or "", cost_cents=cost)
		if resp.status_code >= 400 or not resp.text:
			return _fallback_keywords(text)
		return [k.strip("- •, ") for k in (resp.text or "").split("\n") if k.strip()][:15]
	except Exception:
		return _fallback_keywords(text)


def embed(team: Team, text: str, user=None) -> List[float]:
	try:
		cfg, model_name = _select_provider_and_model(team, capability="embeddings")
		_precheck_limits(cfg, team)
		provider = get_provider(cfg.provider, cfg.api_key, cfg.base_url)
		resp = provider.embed(model=model_name, texts=[text])
    	cost = _compute_cost_cents(cfg.provider, model_name, resp.usage.get("prompt_tokens", 0), resp.usage.get("completion_tokens", 0))
    	_log_usage(team, cfg.provider, model_name, "embeddings", resp.usage.get("prompt_tokens", 0), resp.usage.get("completion_tokens", 0), len(text), 0, resp.status_code < 400, resp.status_code, user=user, request_preview=text, response_preview="[vector]", cost_cents=cost)
		if resp.status_code >= 400 or resp.embeddings is None:
			return _fallback_embedding(text)
		return resp.embeddings or []
	except Exception:
		return _fallback_embedding(text)


def diff_explain(team: Team, old: str, new: str, user=None) -> str:
	try:
		cfg, model_name = _select_provider_and_model(team, capability="text")
		_precheck_limits(cfg, team)
		provider = get_provider(cfg.provider, cfg.api_key, cfg.base_url)
		resp = provider.generate(model=model_name, prompt=f"Erkläre die wichtigsten Änderungen zwischen Version A und B in Stichpunkten.\n\nA:\n{old}\n\nB:\n{new}")
    	cost = _compute_cost_cents(cfg.provider, model_name, resp.usage.get("prompt_tokens", 0), resp.usage.get("completion_tokens", 0))
    	_log_usage(team, cfg.provider, model_name, "diff", resp.usage.get("prompt_tokens", 0), resp.usage.get("completion_tokens", 0), len(old) + len(new), len(resp.text or ""), resp.status_code < 400, resp.status_code, user=user, request_preview=(old[:250] + "\n---\n" + new[:250]), response_preview=resp.text or "", cost_cents=cost)
		if resp.status_code >= 400 or not resp.text:
			return _fallback_diff(old, new)
		return resp.text
	except Exception:
		return _fallback_diff(old, new)


def rerank(team: Team, query: str, documents: List[str], user=None) -> List[int]:
	try:
		cfg, model_name = _select_provider_and_model(team, capability="rerank")
		_precheck_limits(cfg, team)
		provider = get_provider(cfg.provider, cfg.api_key, cfg.base_url)
		joined = "\n\n".join(f"[{i}] {doc[:1000]}" for i, doc in enumerate(documents))
		resp = provider.generate(model=model_name, prompt=f"Gegeben die Query: '{query}'. Ranke die Dokumente [0..N-1] nach Relevanz. Gib nur eine durch Komma getrennte Liste der Indizes aus.\n\n{joined}")
		_log_usage(team, cfg.provider, model_name, "rerank", resp.usage.get("prompt_tokens", 0), resp.usage.get("completion_tokens", 0), len(query) + sum(len(d) for d in documents), len(resp.text or ""), resp.status_code < 400, resp.status_code, user=user)
		if resp.status_code >= 400 or not resp.text:
			return list(range(len(documents)))
		order = []
		for tok in (resp.text or "").replace(" ", "").split(","):
			if tok.isdigit():
				idx = int(tok)
				if 0 <= idx < len(documents):
					order.append(idx)
		return order or list(range(len(documents)))
	except Exception:
		return list(range(len(documents)))


def _fallback_summary(text: str) -> str:
	sentences = [s.strip() for s in text.split(".") if s.strip()]
	return ". ".join(sentences[:3])


def _fallback_keywords(text: str) -> List[str]:
	words = [w.strip(",.;:!?()[]{}\n\t ") for w in text.lower().split()]
	uniq = []
	for w in words:
		if len(w) >= 4 and w not in uniq:
			uniq.append(w)
			if len(uniq) >= 10:
				break
	return uniq


def _fallback_embedding(text: str) -> List[float]:
	seed = sum(ord(c) for c in text) % 1000
	return [(seed + i) / 1000.0 for i in range(128)]


def _fallback_diff(old: str, new: str) -> str:
	return "Geänderte Inhalte vorhanden; detaillierte Erklärung aktuell nicht verfügbar."

