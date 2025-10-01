from __future__ import annotations

import hashlib
import io
import json
from typing import Any, Dict, Optional, Tuple

import httpx
from fastapi import FastAPI, HTTPException
from pdfminer.high_level import extract_text

app = FastAPI(title="Mandari Ingest Service")


def sha256_bytes(data: bytes) -> str:
	return hashlib.sha256(data).hexdigest()


async def fetch_json(url: str, etag: Optional[str] = None, last_modified: Optional[str] = None) -> Tuple[Dict[str, Any], Optional[str], Optional[str], bool]:
    headers = {}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url, headers=headers)
        if r.status_code == 304:
            return {}, etag, last_modified, True
        r.raise_for_status()
        return r.json(), r.headers.get("ETag"), r.headers.get("Last-Modified"), False


@app.get("/health")
async def health() -> Dict[str, str]:
	return {"status": "ok"}


@app.post("/oparl/ingest")
async def ingest_oparl(root: str, tenant_id: int, etag: Optional[str] = None, last_modified: Optional[str] = None) -> Dict[str, Any]:
    try:
        catalog, new_etag, new_lm, not_modified = await fetch_json(root, etag=etag, last_modified=last_modified)
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Katalog fehlerhaft: {e}")
    if not_modified:
        return {"status": "not_modified", "changes": {}}

	# Minimaler Proof: lade bodies und meetings, schreibe über Backend-API
	changes = {"organizations": 0, "meetings": 0, "documents": 0}
	backend = "http://backend:8000/api"
    backoff = 1.0
    async with httpx.AsyncClient(timeout=30.0) as client:
		for body_url in catalog.get("body", []):
            body, _, _, _ = await fetch_json(body_url)
			org = {
				"tenant": tenant_id,
				"name": body.get("name") or body.get("shortName", "Körperschaft"),
				"oparl_id": body.get("id", body_url),
			}
            await client.post(f"{backend}/organizations/", json=org)
			changes["organizations"] += 1

        meetings_list = catalog.get("meeting", [])
		for m_url in meetings_list:
            # Retry mit Backoff für 429/5xx
            for attempt in range(5):
                try:
                    meeting, _, _, _ = await fetch_json(m_url)
                    break
                except httpx.HTTPStatusError as he:
                    if he.response.status_code in (429, 500, 502, 503, 504):
                        import asyncio
                        await asyncio.sleep(backoff)
                        backoff = min(backoff * 2, 10.0)
                        continue
                    raise
            else:
                continue
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

    return {"status": "ok", "changes": changes, "etag": new_etag, "last_modified": new_lm}

