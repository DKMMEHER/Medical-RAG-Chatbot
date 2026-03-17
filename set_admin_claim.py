"""
One-time script to mark a Firebase user as admin.
Run this locally ONCE after creating your users in the Firebase Console.

Usage:
    1. Set FIREBASE_SERVICE_ACCOUNT_JSON env var OR place firebase-service-account.json in this folder
    2. Set ADMIN_USER_UID env var with the actual UID from Firebase Console
    3. Run: uv run python set_admin_claim.py
"""

import os
import json
import firebase_admin
from firebase_admin import auth, credentials

# ── CONFIG ──────────────────────────────────────────────────────────────────
# It's safer to get this from an environment variable than to hardcode it
ADMIN_USER_UID = os.getenv("ADMIN_USER_UID", "zwRD1g1tJHS8SX8I8DkvTpFOkZF2")
# ────────────────────────────────────────────────────────────────────────────


def init_firebase():
    """Initialize Firebase Admin SDK."""
    sa_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        cred = credentials.Certificate(json.loads(sa_json))
    elif os.path.exists("firebase-service-account.json"):
        cred = credentials.Certificate("firebase-service-account.json")
    else:
        raise FileNotFoundError(
            "No Firebase credentials found. Provide FIREBASE_SERVICE_ACCOUNT_JSON "
            "env var or place firebase-service-account.json in this folder."
        )
    firebase_admin.initialize_app(cred)


def set_admin(uid: str):
    """Set admin: True custom claim on a Firebase user."""
    auth.set_custom_user_claims(uid, {"admin": True})
    user = auth.get_user(uid)
    print(f"✅ Admin role granted to: {user.email} (uid={uid})")
    print(f"   Custom claims: {user.custom_claims}")


if __name__ == "__main__":
    init_firebase()
    set_admin(ADMIN_USER_UID)
