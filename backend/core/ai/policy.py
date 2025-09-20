from __future__ import annotations

import re
from typing import Tuple

from ..models import AIPolicy, Team


PII_REGEXES = [
	re.compile(r"\b\d{2,3}[- ]?\d{3,}[- ]?\d{2,}\b"),
	re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
	re.compile(r"\b\d{11}\b"),
]


def apply_policies(team: Team, text: str) -> Tuple[str, bool]:
	policy = AIPolicy.objects.filter(team=team).first()
	if not policy:
		return text, True

	if policy.pii_masking_enabled:
		for rx in PII_REGEXES:
			text = rx.sub("[PII]", text)

	allow = True
	if not policy.allow_external_transfer and policy.anonymize_before_send:
		allow = True
	elif not policy.allow_external_transfer and not policy.anonymize_before_send:
		allow = False

	return text, allow

