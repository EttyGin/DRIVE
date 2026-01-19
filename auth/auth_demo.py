"""
auth_demo.py
============

Single-file demo for:
- Authorization parsing
- Bearer vs Api-Key
- Hashed API keys (HMAC)
- Admin-only API key overwrite (user-defined value)
"""

import hmac
import hashlib
from dataclasses import dataclass
from typing import Optional


# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

API_KEY_HMAC_SECRET = b"server-side-secret-only-backend-knows"


# -------------------------------------------------------------------
# Models (in-memory DB simulation)
# -------------------------------------------------------------------

@dataclass
class LocalUser:
    id: int
    username: str
    role: str  # "admin" | "regular"
    api_key_hash: Optional[str] = None


# Fake DB
DB = {
    "local_users": []
}


# -------------------------------------------------------------------
# Errors
# -------------------------------------------------------------------

class AuthError(Exception):
    pass


# -------------------------------------------------------------------
# Hashing
# -------------------------------------------------------------------

def hash_api_key(raw_key: str) -> str:
    return hmac.new(
        API_KEY_HMAC_SECRET,
        raw_key.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# -------------------------------------------------------------------
# Authorization parsing
# -------------------------------------------------------------------

def parse_authorization_header(auth_header: Optional[str]):
    if not auth_header:
        raise AuthError("Missing Authorization header")

    try:
        scheme, value = auth_header.split(" ", 1)
    except ValueError:
        raise AuthError("Invalid Authorization header format")

    return scheme.lower(), value.strip()


# -------------------------------------------------------------------
# Authentication
# -------------------------------------------------------------------

def authenticate_request(auth_header: str):
    scheme, value = parse_authorization_header(auth_header)

    if scheme == "bearer":
        return authenticate_oidc(value)

    if scheme == "api-key":
        return authenticate_api_key(value)

    raise AuthError("Unsupported authorization scheme")


def authenticate_oidc(token: str):
    """
    Dummy OIDC auth.
    In real life: verify JWT, fetch claims, map to user.
    """
    if token != "valid-oidc-token":
        raise AuthError("Invalid OIDC token")

    return {
        "type": "oidc",
        "sub": "oidc-user-123",
        "role": "user",
    }


def authenticate_api_key(raw_key: str) -> LocalUser:
    key_hash = hash_api_key(raw_key)

    for user in DB["local_users"]:
        if user.api_key_hash == key_hash:
            return user

    raise AuthError("Invalid API key")


# -------------------------------------------------------------------
# Admin-only API key overwrite
# -------------------------------------------------------------------

def set_api_key_for_user(
    acting_user: LocalUser,
    target_user_id: int,
    new_raw_api_key: str,
):
    if acting_user.role != "admin":
        raise AuthError("Admin privileges required")

    if not new_raw_api_key or len(new_raw_api_key) < 20:
        raise ValueError("API key too short")

    target_user = next(
        (u for u in DB["local_users"] if u.id == target_user_id),
        None,
    )

    if not target_user:
        raise ValueError("Target user not found")

    target_user.api_key_hash = hash_api_key(new_raw_api_key)


# -------------------------------------------------------------------
# Demo / manual test
# -------------------------------------------------------------------

if __name__ == "__main__":
    # Create two local users
    admin = LocalUser(id=1, username="admin", role="admin")
    regular = LocalUser(id=2, username="service", role="regular")

    DB["local_users"].extend([admin, regular])

    # Admin sets API keys (user-defined)
    set_api_key_for_user(
        acting_user=admin,
        target_user_id=1,
        new_raw_api_key="ADMIN_SUPER_SECRET_KEY_123456",
    )

    set_api_key_for_user(
        acting_user=admin,
        target_user_id=2,
        new_raw_api_key="REGULAR_SERVICE_KEY_abcdef",
    )

    print("=== Stored hashes ===")
    for u in DB["local_users"]:
        print(u.username, u.api_key_hash)

    print("\n=== Auth tests ===")

    # API key auth
    user = authenticate_request(
        "Authorization: Api-Key REGULAR_SERVICE_KEY_abcdef"
        .replace("Authorization: ", "")
    )
    print("Authenticated via API key:", user.username, user.role)

    # OIDC auth
    oidc_user = authenticate_request(
        "Authorization: Bearer valid-oidc-token"
        .replace("Authorization: ", "")
    )
    print("Authenticated via OIDC:", oidc_user)

    # Invalid key
    try:
        authenticate_request(
            "Authorization: Api-Key WRONG_KEY"
            .replace("Authorization: ", "")
        )
    except AuthError as e:
        print("Auth failed as expected:", e)
