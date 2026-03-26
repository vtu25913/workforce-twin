from flask import Blueprint, request, jsonify
from auth_utils import admin_required
from database import db, User, Simulation
from werkzeug.security import generate_password_hash

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/users")
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])


@admin_bp.post("/users")
@admin_required
def create_user():
    data = request.get_json(silent=True) or {}
    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or "Welcome@123"
    role     = data.get("role", "analyst")
    org      = data.get("org", "Demo Corp")

    if not name or not email:
        return jsonify({"error": "name and email required"}), 400
    if role not in ("admin", "analyst", "viewer"):
        return jsonify({"error": "Invalid role"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(
        name=name, email=email,
        password_hash=generate_password_hash(password),
        role=role, org=org
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@admin_bp.patch("/users/<int:uid>")
@admin_required
def update_user(uid):
    user = User.query.get_or_404(uid)
    data = request.get_json(silent=True) or {}

    if "role" in data:
        if data["role"] not in ("admin", "analyst", "viewer"):
            return jsonify({"error": "Invalid role"}), 400
        user.role = data["role"]
    if "is_active" in data:
        user.is_active = bool(data["is_active"])
    if "name" in data:
        user.name = data["name"]
    if "org" in data:
        user.org = data["org"]

    db.session.commit()
    return jsonify(user.to_dict())


@admin_bp.delete("/users/<int:uid>")
@admin_required
def delete_user(uid):
    user = User.query.get_or_404(uid)
    if user.email in ("admin@twin.ai",):
        return jsonify({"error": "Cannot delete the default admin"}), 403
    Simulation.query.filter_by(user_id=uid).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})


@admin_bp.get("/stats")
@admin_required
def stats():
    return jsonify({
        "total_users":       User.query.count(),
        "active_users":      User.query.filter_by(is_active=True).count(),
        "total_simulations": Simulation.query.count(),
        "completed_sims":    Simulation.query.filter_by(status="completed").count(),
        "admins":            User.query.filter_by(role="admin").count(),
        "analysts":          User.query.filter_by(role="analyst").count(),
        "viewers":           User.query.filter_by(role="viewer").count(),
    })
