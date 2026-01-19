from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from dataclasses import dataclass
from typing import Optional
import hmac
import hashlib

# -------------------------------------------------
# Config
# -------------------------------------------------

API_KEY_HMAC_SECRET = b"server-side-secret-only-backend-knows"

app = FastAPI(title="Auth Demo API (Self API Key Change)")


# -------------------------------------------------
# Models (in-memory DB)
# -------------------------------------------------

@dataclass
class LocalUser:
    id: int
    username: str
    role: str  # "admin" | "regular"
    api_key_hash: Optional[str] = None


DB = {
    "local_users": []
}


# -------------------------------------------------
# Errors
# -------------------------------------------------

class AuthError(Exception):
    pass


# -------------------------------------------------
# Hashing
# -------------------------------------------------

def hash_api_key(raw_key: str) -> str:
    return hmac.new(
        API_KEY_HMAC_SECRET,
        raw_key.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# -------------------------------------------------
# Authorization parsing
# -------------------------------------------------

def parse_authorization_header(auth_header: Optional[str]):
    if not auth_header:
        raise AuthError("Missing Authorization header")

    try:
        scheme, value = auth_header.split(" ", 1)
    except ValueError:
        raise AuthError("Invalid Authorization header format")

    return scheme.lower(), value.strip()


# -------------------------------------------------
# Authentication
# -------------------------------------------------

def authenticate_request(request: Request):
    auth_header = request.headers.get("Authorization")

    try:
        scheme, value = parse_authorization_header(auth_header)

        if scheme == "bearer":
            return authenticate_oidc(value)

        if scheme == "api-key":
            return authenticate_api_key(value)

        raise AuthError("Unsupported authorization scheme")

    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))


def authenticate_oidc(token: str):
    # Dummy OIDC
    if token != "valid-oidc-token":
        raise AuthError("Invalid OIDC token")

    return {
        "auth_type": "oidc",
        "sub": "oidc-user-123",
        "role": "user",
    }


def authenticate_api_key(raw_key: str) -> LocalUser:
    key_hash = hash_api_key(raw_key)

    for user in DB["local_users"]:
        if user.api_key_hash == key_hash:
            return user

    raise AuthError("Invalid API key")


# -------------------------------------------------
# API Key self-change
# -------------------------------------------------

class ApiKeyChangeRequest(BaseModel):
    new_api_key: str


@app.post("/me/change-api-key")
def change_my_api_key(
    payload: ApiKeyChangeRequest,
    user=Depends(authenticate_request),
):
    if not isinstance(user, LocalUser):
        raise HTTPException(
            status_code=403,
            detail="Only local users can change API keys",
        )

    if not payload.new_api_key or len(payload.new_api_key) < 20:
        raise HTTPException(
            status_code=400,
            detail="API key too short",
        )

    user.api_key_hash = hash_api_key(payload.new_api_key)

    return {"status": "api key updated"}


# -------------------------------------------------
# Utility
# -------------------------------------------------

@app.get("/me")
def who_am_i(user=Depends(authenticate_request)):
    if isinstance(user, LocalUser):
        return {
            "auth_type": "api-key",
            "username": user.username,
            "role": user.role,
        }

    return user


# -------------------------------------------------
# Bootstrap demo data
# -------------------------------------------------

def bootstrap():
    admin = LocalUser(
        id=1,
        username="admin",
        role="admin",
        api_key_hash=hash_api_key("ADMIN_SUPER_SECRET_KEY_123456"),
    )

    regular = LocalUser(
        id=2,
        username="service",
        role="regular",
        api_key_hash=hash_api_key("REGULAR_SERVICE_KEY_abcdef"),
    )

    DB["local_users"].extend([admin, regular])


bootstrap()
