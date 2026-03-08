"""
Firebase Authentication Module for Medical Chatbot.

Handles:
- Firebase Admin SDK initialization (server-side token verification)
- User sign-in via Firebase REST API (email/password)
- ID token verification and admin role checking
"""

import os
import json
import requests
import firebase_admin
from firebase_admin import auth, credentials

_firebase_app = None


def init_firebase() -> None:
    """Initialize Firebase Admin SDK (idempotent — safe to call multiple times)."""
    global _firebase_app
    if _firebase_app is not None:
        return

    sa_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        cred = credentials.Certificate(json.loads(sa_json))
    elif os.path.exists("firebase-service-account.json"):
        cred = credentials.Certificate("firebase-service-account.json")
    else:
        raise EnvironmentError(
            "Firebase credentials not found. Set FIREBASE_SERVICE_ACCOUNT_JSON env var "
            "or place firebase-service-account.json in the project root."
        )
    _firebase_app = firebase_admin.initialize_app(cred)


def sign_in(email: str, password: str) -> dict:
    """
    Sign in a user with email + password via Firebase REST API.

    Returns:
        dict with keys: id_token, refresh_token, email, local_id (uid)

    Raises:
        ValueError: if credentials are invalid
        RuntimeError: if the FIREBASE_API_KEY env var is missing
    """
    api_key = os.getenv("FIREBASE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "FIREBASE_API_KEY environment variable is not set. "
            "Get it from Firebase Console → Project Settings → General → Web API Key."
        )

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}

    resp = requests.post(url, json=payload, timeout=10)
    data = resp.json()

    if "error" in data:
        error_msg = data["error"].get("message", "Unknown error")
        if error_msg in (
            "EMAIL_NOT_FOUND",
            "INVALID_PASSWORD",
            "INVALID_LOGIN_CREDENTIALS",
        ):
            raise ValueError("Invalid email or password. Please try again.")
        raise ValueError(f"Authentication error: {error_msg}")

    return {
        "id_token": data["idToken"],
        "refresh_token": data["refreshToken"],
        "email": data["email"],
        "uid": data["localId"],
    }


def verify_token(id_token: str) -> dict:
    """
    Verify a Firebase ID token server-side and return decoded user info.

    Returns:
        dict with keys: uid, email, is_admin, name
    """
    decoded = auth.verify_id_token(id_token)
    claims = decoded.get("admin", False)
    return {
        "uid": decoded["uid"],
        "email": decoded.get("email", ""),
        "is_admin": bool(claims),
        "name": decoded.get("name", decoded.get("email", "User")),
    }


def is_admin_user(id_token: str) -> bool:
    """Quick helper to check admin status from an ID token."""
    try:
        user_info = verify_token(id_token)
        return user_info["is_admin"]
    except Exception:
        return False
