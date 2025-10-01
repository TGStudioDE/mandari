from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
import jwt
import os
from datetime import datetime, timezone


def _jwt_decode(token: str) -> dict:
	secret = os.getenv("JWT_SECRET", os.getenv("DJANGO_SECRET_KEY", "insecure"))
	audience = os.getenv("JWT_AUDIENCE", "mandari-api")
	try:
		return jwt.decode(token, secret, algorithms=["HS256"], audience=audience)
	except Exception as e:
		raise exceptions.AuthenticationFailed(str(e))


class CsrfExemptSessionAuthentication(SessionAuthentication):
	def enforce_csrf(self, request):
		return


class JWTAuthentication(BaseAuthentication):
	"""Einfache JWT-Auth: Erwartet Authorization: Bearer <token>."""

	def authenticate(self, request):
		auth_header = request.headers.get("Authorization") or ""
		if not auth_header.startswith("Bearer "):
			return None
		try:
			token = auth_header.split(" ", 1)[1].strip()
			payload = _jwt_decode(token)
			user_id = payload.get("sub")
			org_id = payload.get("org_id")
			if not user_id:
				raise exceptions.AuthenticationFailed("sub fehlt")
			User = get_user_model()
			user = User.objects.filter(id=user_id).first()
			if not user:
				raise exceptions.AuthenticationFailed("User nicht gefunden")
			# Optional: org-scope prüfen
			if org_id and getattr(user, "tenant_id", None) and user.tenant_id != int(org_id):
				raise exceptions.AuthenticationFailed("Org-Scope ungültig")
			# Token-Ablauf prüfen (PyJWT prüft exp automatisch, aber sicherheitshalber)
			exp = payload.get("exp")
			if exp and datetime.fromtimestamp(int(exp), tz=timezone.utc) < datetime.now(tz=timezone.utc):
				raise exceptions.AuthenticationFailed("Token abgelaufen")
			# Scopes kann der View prüfen (payload["scopes"]) via request.auth
			return (user, payload)
		except exceptions.AuthenticationFailed:
			raise
		except Exception as e:
			raise exceptions.AuthenticationFailed(str(e))


