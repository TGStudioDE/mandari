from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .models import Meeting


def export_meetings_ics(meetings: Iterable[Meeting]) -> str:
	lines = [
		"BEGIN:VCALENDAR",
		"VERSION:2.0",
		"PRODID:-//Mandari//EN",
	]
	for m in meetings:
		start = m.start.strftime("%Y%m%dT%H%M%SZ")
		end = (m.end or m.start).strftime("%Y%m%dT%H%M%SZ")
		uid = f"meeting-{m.id}@mandari"
		summary = f"{m.committee.name} Sitzung"
		lines.extend([
			"BEGIN:VEVENT",
			f"UID:{uid}",
			f"DTSTART:{start}",
			f"DTEND:{end}",
			f"SUMMARY:{summary}",
			"END:VEVENT",
		])
	lines.append("END:VCALENDAR")
	return "\r\n".join(lines)

