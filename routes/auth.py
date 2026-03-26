from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User
from auth_utils import create_token, login_required
import re

auth_bp = Blueprint("auth", __name__)


def _validate_email(email):
    return re.match(r"^[\w.+-]+@[\w-]+\.[a-z]{2,}$", email, re.I)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    org      = (data.get("org") or "My Organisation").strip()

    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required"}), 400
    if not _validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        name=name, email=email,
        password_hash=generate_password_hash(password),
        role="viewer", org=org
    )
    db.session.add(user)
    db.session.commit()

    token = create_token(user.id, user.role)
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data     = request.get_json(silent=True) or {}
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401
    if not user.is_active:
        return jsonify({"error": "Account disabled. Contact your admin."}), 403

    token = create_token(user.id, user.role)
    return jsonify({"token": token, "user": user.to_dict()})


@auth_bp.get("/me")
@login_required
def me():
    return jsonify({"user": request.current_user.to_dict()})


@auth_bp.post("/change-password")
@login_required
def change_password():
    data        = request.get_json(silent=True) or {}
    old_pw      = data.get("old_password") or ""
    new_pw      = data.get("new_password") or ""
    user        = request.current_user

    if not check_password_hash(user.password_hash, old_pw):
        return jsonify({"error": "Current password is incorrect"}), 400
    if len(new_pw) < 8:
        return jsonify({"error": "New password must be at least 8 characters"}), 400

    user.password_hash = generate_password_hash(new_pw)
    db.session.commit()
    return jsonify({"message": "Password updated successfully"})
