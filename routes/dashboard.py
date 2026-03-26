from flask import Blueprint, jsonify, request
from auth_utils import login_required
from database import db, Simulation, User
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/summary")
@login_required
def summary():
    user = request.current_user

    # Admins see all sims; others see only their own
    q = Simulation.query if user.role == "admin" else Simulation.query.filter_by(user_id=user.id)

    total_sims   = q.count()
    completed    = q.filter_by(status="completed").count()
    last_sim     = q.order_by(Simulation.created_at.desc()).first()

    last_adoption = None
    last_risk     = None
    if last_sim and last_sim.result():
        r             = last_sim.result()
        last_adoption = r.get("final_adoption")
        last_risk     = r.get("risk")

    return jsonify({
        "total_simulations":   total_sims,
        "completed":           completed,
        "last_adoption":       last_adoption,
        "last_risk":           last_risk,
        "workforce_size":      1240,
        "active_personas":     5,
        "data_sources":        12,
    })


@dashboard_bp.get("/recent-simulations")
@login_required
def recent_simulations():
    user = request.current_user
    q = Simulation.query if user.role == "admin" else Simulation.query.filter_by(user_id=user.id)
    sims = q.order_by(Simulation.created_at.desc()).limit(10).all()
    return jsonify([s.to_dict() for s in sims])


@dashboard_bp.get("/telemetry")
@login_required
def telemetry():
    import random, math
    months = ["Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun"]
    def wave(base, peak):
        return [round(base + (peak-base)*(i/11) + (random.random()-0.5)*6) for i in range(12)]
    return jsonify({
        "months":   months,
        "messaging": wave(55,88),
        "calendar":  wave(38,72),
        "ticketing": wave(18,42),
    })
