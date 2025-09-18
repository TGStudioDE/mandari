from __future__ import annotations

import re
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI(title="Mandari AI Service")


class SummaryRequest(BaseModel):
	text: str
	max_words: int = 120


_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def anonymize(text: str) -> str:
	patterns = [
		(r"\b\d{2,3}-\d{7,}\b", "[TEL]"),
		(r"[\w\.-]+@[\w\.-]+", "[EMAIL]"),
		(r"\b\d{2}\.\d{2}\.\d{4}\b", "[DATE]"),
	]
	for pat, repl in patterns:
		text = re.sub(pat, repl, text)
	return text


@app.get("/health")
async def health() -> Dict[str, str]:
	return {"status": "ok"}


@app.post("/summary")
async def summary(req: SummaryRequest) -> Dict[str, Any]:
	text = anonymize(req.text)
	max_char = max(80, req.max_words * 6)
	result = _summarizer(text, max_length=min(512, req.max_words * 3), min_length=30, do_sample=False)
	return {"summary": result[0]["summary_text"][:max_char]}

