from __future__ import annotations

from rest_framework import permissions, status, views
from rest_framework.response import Response

from ..models import AIFeatureFlag, Team
from .policy import apply_policies
from .runtime import summarize as do_summarize, keywords as do_keywords, embed as do_embed, diff_explain as do_diff, rerank as do_rerank


def _feature_enabled(team: Team, name: str) -> bool:
	flag = AIFeatureFlag.objects.filter(team=team, name=name).first()
	return True if not flag else flag.enabled


class BaseTeamAIView(views.APIView):
	permission_classes = [permissions.IsAuthenticated]

	def _get_team(self, request) -> Team:
		team_id = request.data.get("team") or request.query_params.get("team")
		return Team.objects.get(id=team_id)


class SummarizeView(BaseTeamAIView):
	def post(self, request, *args, **kwargs):
		team = self._get_team(request)
		if not _feature_enabled(team, "summarize"):
			return Response({"error": "Feature deaktiviert"}, status=status.HTTP_403_FORBIDDEN)
		text = request.data.get("text", "")
		masked, allow = apply_policies(team, text)
		if not allow:
			return Response({"error": "Externe Übertragung nicht erlaubt"}, status=status.HTTP_403_FORBIDDEN)
		out = do_summarize(team, masked, user=request.user)
		return Response({"summary": out})


class KeywordsView(BaseTeamAIView):
	def post(self, request, *args, **kwargs):
		team = self._get_team(request)
		if not _feature_enabled(team, "keywords"):
			return Response({"error": "Feature deaktiviert"}, status=status.HTTP_403_FORBIDDEN)
		text = request.data.get("text", "")
		masked, allow = apply_policies(team, text)
		if not allow:
			return Response({"error": "Externe Übertragung nicht erlaubt"}, status=status.HTTP_403_FORBIDDEN)
		out = do_keywords(team, masked, user=request.user)
		return Response({"keywords": out})


class EmbeddingsView(BaseTeamAIView):
	def post(self, request, *args, **kwargs):
		team = self._get_team(request)
		if not _feature_enabled(team, "embeddings"):
			return Response({"error": "Feature deaktiviert"}, status=status.HTTP_403_FORBIDDEN)
		text = request.data.get("text", "")
		masked, allow = apply_policies(team, text)
		if not allow:
			return Response({"error": "Externe Übertragung nicht erlaubt"}, status=status.HTTP_403_FORBIDDEN)
		vec = do_embed(team, masked, user=request.user)
		return Response({"embedding": vec})


class DiffExplainView(BaseTeamAIView):
	def post(self, request, *args, **kwargs):
		team = self._get_team(request)
		if not _feature_enabled(team, "diff_explain"):
			return Response({"error": "Feature deaktiviert"}, status=status.HTTP_403_FORBIDDEN)
		old = request.data.get("old", "")
		new = request.data.get("new", "")
		old_masked, allow_old = apply_policies(team, old)
		new_masked, allow_new = apply_policies(team, new)
		if not (allow_old and allow_new):
			return Response({"error": "Externe Übertragung nicht erlaubt"}, status=status.HTTP_403_FORBIDDEN)
		out = do_diff(team, old_masked, new_masked, user=request.user)
		return Response({"explanation": out})


class RerankView(BaseTeamAIView):
	def post(self, request, *args, **kwargs):
		team = self._get_team(request)
		if not _feature_enabled(team, "rerank"):
			return Response({"error": "Feature deaktiviert"}, status=status.HTTP_403_FORBIDDEN)
		query = request.data.get("query", "")
		documents = request.data.get("documents", []) or []
		# Policy: Query und Dokumente maskieren bevor sie ggf. versendet werden
		q_masked, allow_q = apply_policies(team, query)
		masked_docs = []
		allow_docs = True
		for d in documents:
			m, a = apply_policies(team, d)
			masked_docs.append(m)
			allow_docs = allow_docs and a
		if not (allow_q and allow_docs):
			return Response({"error": "Externe Übertragung nicht erlaubt"}, status=status.HTTP_403_FORBIDDEN)
		order = do_rerank(team, q_masked, masked_docs, user=request.user)
		return Response({"order": order})

