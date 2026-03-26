from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(180), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20), nullable=False, default="analyst")
    org           = db.Column(db.String(120), default="Default Org")
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    is_active     = db.Column(db.Boolean, default=True)

    simulations   = db.relationship("Simulation", backref="owner", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "org": self.org,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
        }


class Simulation(db.Model):
    __tablename__ = "simulations"
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name             = db.Column(db.String(200), nullable=False)
    tool_change      = db.Column(db.String(100))
    rollout_strategy = db.Column(db.String(100))
    cm_support       = db.Column(db.String(100))
    horizon_days     = db.Column(db.Integer, default=90)
    workforce_size   = db.Column(db.Integer, default=1240)
    resist_baseline  = db.Column(db.Float, default=35.0)
    train_effectiveness = db.Column(db.Float, default=60.0)
    result_json      = db.Column(db.Text, nullable=True)
    status           = db.Column(db.String(20), default="pending")
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    def result(self):
        return json.loads(self.result_json) if self.result_json else None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "tool_change": self.tool_change,
            "rollout_strategy": self.rollout_strategy,
            "cm_support": self.cm_support,
            "horizon_days": self.horizon_days,
            "workforce_size": self.workforce_size,
            "resist_baseline": self.resist_baseline,
            "train_effectiveness": self.train_effectiveness,
            "result": self.result(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "owner_name": self.owner.name if self.owner else "—",
        }


# ─── INIT ─────────────────────────────────────────────────────────────────────

def init_db():
    db.create_all()
    _seed_default_users()


def _seed_default_users():
    from werkzeug.security import generate_password_hash
    defaults = [
        dict(name="Admin User",    email="admin@twin.ai",   password="Admin@123",   role="admin"),
        dict(name="Alice Analyst", email="analyst@twin.ai", password="Analyst@123", role="analyst"),
        dict(name="Bob Viewer",    email="viewer@twin.ai",  password="Viewer@123",  role="viewer"),
    ]
    for u in defaults:
        if not User.query.filter_by(email=u["email"]).first():
            user = User(
                name=u["name"],
                email=u["email"],
                password_hash=generate_password_hash(u["password"]),
                role=u["role"],
                org="Demo Corp",
                is_active=True
            )
            db.session.add(user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()