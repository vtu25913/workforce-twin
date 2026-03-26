import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from database import User


def create_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(
            hours=current_app.config.get("JWT_EXPIRY_HOURS", 8)
        ),
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    # PyJWT >= 2.0 returns str, older versions return bytes
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_token(token: str):
    return jwt.decode(
        token,
        current_app.config["SECRET_KEY"],
        algorithms=["HS256"],
        options={"verify_exp": True}
    )


def _get_current_user():
    # Check multiple header formats Railway might use
    auth = request.headers.get("Authorization", "")
    if not auth:
        auth = request.headers.get("HTTP_AUTHORIZATION", "")
    if not auth:
        auth = request.environ.get("HTTP_AUTHORIZATION", "")

    if not auth.startswith("Bearer "):
        return None, "Missing or malformed token"

    token = auth.split(" ", 1)[1].strip()
    if not token:
        return None, "Empty token"

    try:
        data = decode_token(token)
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError as e:
        return None, f"Invalid token: {str(e)}"

    user_id = data.get("sub")
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None, "Invalid token payload"

    user = User.query.get(user_id)
    if not user or not user.is_active:
        return None, "User not found or inactive"
    return user, None


# ─── DECORATORS ───────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user, err = _get_current_user()
        if err:
            return jsonify({"error": err}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return wrapper


def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user, err = _get_current_user()
            if err:
                return jsonify({"error": err}), 401
            if user.role not in allowed_roles:
                return jsonify({"error": f"Access denied. Required roles: {list(allowed_roles)}"}), 403
            request.current_user = user
            return f(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(f):
    return roles_required("admin")(f)