from firebase_admin import auth
from src.auth.firebase_auth import init_firebase

# Disable noise
import logging

logging.getLogger("firebase_admin").setLevel(logging.WARNING)


def list_admin_users():
    """
    Lists all Firebase users and checks for their 'admin' custom claim.
    Uses the project's existing initialization logic.
    """
    try:
        # Use the app's existing robust initialization
        init_firebase()
    except Exception as e:
        print(f"❌ Firebase Initialization Error: {e}")
        return

    print("\n" + "=" * 85)
    print(f"{'Email':<35} | {'Admin Status':<12} | {'UID'}")
    print("=" * 85)

    try:
        # List all users
        page = auth.list_users()
        count = 0
        admin_count = 0

        while page:
            for user in page.users:
                count += 1
                # Check for the 'admin' custom claim
                is_admin = (
                    user.custom_claims.get("admin", False)
                    if user.custom_claims
                    else False
                )

                if is_admin:
                    admin_count += 1
                    status = "✅ ADMIN"
                else:
                    status = "❌ User"

                print(f"{user.email:<35} | {status:<12} | {user.uid}")

            page = page.get_next_page()

        print("=" * 85)
        print(f"📊 Summary: {count} total users, {admin_count} administrators.")
        print("=" * 85 + "\n")

    except Exception as e:
        print(f"❌ Error listing users: {e}")


if __name__ == "__main__":
    list_admin_users()
