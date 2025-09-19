from __future__ import annotations

import asyncio
import hashlib
import io
import json
import mimetypes
from typing import Any, Dict, Optional, Tuple

import httpx
from fastapi import FastAPI, HTTPException
from pdfminer.high_level import extract_text

app = FastAPI(title="Mandari Ingest Service")
REQUEST_BACKOFF_BASE_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 30.0


def sha256_bytes(data: bytes) -> str:
	return hashlib.sha256(data).hexdigest()


async def fetch_json(url: str, headers: Optional[Dict[str, str]] = None, etag: Optional[str] = None, last_modified: Optional[str] = None, timeout: float = 30.0, max_retries: int = 3) -> Tuple[Optional[Dict[str, Any]], Dict[str, str]]:
	req_headers = headers.copy() if headers else {}
	if etag:
		req_headers["If-None-Match"] = etag
	if last_modified:
		req_headers["If-Modified-Since"] = last_modified
	attempt = 0
	backoff = REQUEST_BACKOFF_BASE_SECONDS
	async with httpx.AsyncClient(timeout=timeout) as client:
		while True:
			try:
				r = await client.get(url, headers=req_headers)
				if r.status_code == 304:
					return None, {"etag": r.headers.get("ETag", ""), "last_modified": r.headers.get("Last-Modified", "")}
				r.raise_for_status()
				return r.json(), {"etag": r.headers.get("ETag", ""), "last_modified": r.headers.get("Last-Modified", "")}
			except Exception:
				attempt += 1
				if attempt > max_retries:
					raise
				await asyncio.sleep(min(backoff, MAX_BACKOFF_SECONDS))
				backoff *= 2


@app.get("/health")
async def health() -> Dict[str, str]:
	return {"status": "ok"}


@app.post("/oparl/ingest")
async def ingest_oparl(root: str, tenant_id: int, source_id: Optional[int] = None, source_base: Optional[str] = None) -> Dict[str, Any]:
	try:
		catalog, cat_headers = await fetch_json(root)
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Katalog fehlerhaft: {e}")

	changes = {"organizations": 0, "meetings": 0, "documents": 0}
	backend = "http://backend:8000/api"
	async with httpx.AsyncClient(timeout=30.0) as client:
		if source_id and (cat_headers.get("etag") or cat_headers.get("last_modified")):
			try:
				await client.patch(
					f"{backend}/oparl-sources/{source_id}/",
					json={
						"etag": cat_headers.get("etag", ""),
						"last_modified": cat_headers.get("last_modified", ""),
					},
				)
			except Exception:
				pass
		for body_url in catalog.get("body", []):
			body, _ = await fetch_json(body_url)
			org = {
				"tenant": tenant_id,
				"name": body.get("name") or body.get("shortName", "Körperschaft"),
				"oparl_id": body.get("id", body_url),
				"source_base": source_base or root,
				"raw": body,
			}
			await client.post(f"{backend}/organizations/", json=org)
			changes["organizations"] += 1

		meetings_list = catalog.get("meeting", [])
		for m_url in meetings_list:
			meeting, _ = await fetch_json(m_url)
			committee_name = (meeting.get("committee") or {}).get("name", "Ausschuss") if isinstance(meeting.get("committee"), dict) else "Ausschuss"
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
					"source_base": source_base or root,
					"raw": meeting,
				},
			)
			meeting_id = mr.json()["id"]
			changes["meetings"] += 1

			for f_url in meeting.get("auxiliaryFile", []):
				try:
					fr = await client.get(f_url)
					fr.raise_for_status()
					content = fr.content
					content_hash = sha256_bytes(content)
					mime, _ = mimetypes.guess_type(f_url)
					if not mime:
						mime = fr.headers.get("Content-Type", "application/octet-stream").split(";")[0]
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
							"source_base": source_base or root,
							"mimetype": mime,
						},
					)
					changes["documents"] += 1
				except Exception:
					continue

	return {"status": "ok", "changes": changes}

