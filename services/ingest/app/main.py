from __future__ import annotations

import hashlib
import io
import json
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pdfminer.high_level import extract_text

app = FastAPI(title="Mandari Ingest Service")


def sha256_bytes(data: bytes) -> str:
	return hashlib.sha256(data).hexdigest()


async def fetch_json(url: str) -> Dict[str, Any]:
	async with httpx.AsyncClient(timeout=30.0) as client:
		r = await client.get(url)
		r.raise_for_status()
		return r.json()


@app.get("/health")
async def health() -> Dict[str, str]:
	return {"status": "ok"}


@app.post("/oparl/ingest")
async def ingest_oparl(root: str, tenant_id: int) -> Dict[str, Any]:
	try:
		catalog = await fetch_json(root)
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Katalog fehlerhaft: {e}")

	# Minimaler Proof: lade bodies und meetings, schreibe über Backend-API
	changes = {"organizations": 0, "meetings": 0, "documents": 0}
	backend = "http://backend:8000/api"
	async with httpx.AsyncClient(timeout=30.0) as client:
		for body_url in catalog.get("body", []):
			body = await fetch_json(body_url)
			org = {
				"tenant": tenant_id,
				"name": body.get("name") or body.get("shortName", "Körperschaft"),
				"oparl_id": body.get("id", body_url),
			}
			await client.post(f"{backend}/organizations/", json=org)
			changes["organizations"] += 1

		meetings_list = catalog.get("meeting", [])
		for m_url in meetings_list:
			meeting = await fetch_json(m_url)
			committee_name = (meeting.get("committee") or {}).get("name", "Ausschuss") if isinstance(meeting.get("committee"), dict) else "Ausschuss"
			# Upsert Committee by name (idempotent Demo)
			r = await client.get(f"{backend}/committees/?tenant={tenant_id}")
			committee_id: Optional[int] = None
			for c in r.json():
				if c["name"] == committee_name:
					committee_id = c["id"]
					break
			if committee_id is None:
				cr = await client.post(f"{backend}/committees/", json={"tenant": tenant_id, "name": committee_name})
				committee_id = cr.json()["id"]

			start = meeting.get("start") or meeting.get("startDate") or meeting.get("date")
			mr = await client.post(
				f"{backend}/meetings/",
				json={
					"tenant": tenant_id,
					"committee": committee_id,
					"start": start,
					"oparl_id": meeting.get("id", m_url),
				},
			)
			meeting_id = mr.json()["id"]
			changes["meetings"] += 1

			# Documents: fetch files if linked as URL in meeting
			for f_url in meeting.get("auxiliaryFile", []):
				try:
					fr = await client.get(f_url)
					fr.raise_for_status()
					content = fr.content
					content_hash = sha256_bytes(content)
					try:
						text = extract_text(io.BytesIO(content))
					except Exception:
						text = ""
					await client.post(
						f"{backend}/documents/",
						json={
							"tenant": tenant_id,
							"title": f"Dokument {content_hash[:8]}",
							"raw": {"source": f_url},
							"normalized": {},
							"content_text": text[:10000],
							"content_hash": content_hash,
							"oparl_id": f_url,
						},
					)
					changes["documents"] += 1
				except Exception:
					continue

	return {"status": "ok", "changes": changes}

