from flask import Blueprint, request, jsonify
from auth_utils import login_required, roles_required
from database import db, Simulation
import math, json, random

simulate_bp = Blueprint("simulate", __name__)

# ─── SIMULATION ENGINE ─────────────────────────────────────────────────────────

PERSONAS = [
    {"id":"power",  "pct":18, "adoption_speed":92, "resistance":8,  "collab":85},
    {"id":"collab", "pct":24, "adoption_speed":70, "resistance":20, "collab":95},
    {"id":"steady", "pct":29, "adoption_speed":55, "resistance":38, "collab":60},
    {"id":"resist", "pct":15, "adoption_speed":25, "resistance":75, "collab":40},
    {"id":"remote", "pct":14, "adoption_speed":78, "resistance":18, "collab":72},
]

TOOL_BOOST  = {"teams":5, "ticketing":10, "hybrid":3, "consolidation":-8, "ai_assist":12, "mdm":0}
STRAT_BOOST = {"big_bang":-6, "phased":9, "pilot":13, "opt_in":5}
CM_BOOST    = {"none":0, "basic":8, "medium":18, "high":30}


def run_abm(params: dict) -> dict:
    tool     = params.get("tool_change", "teams")
    strategy = params.get("rollout_strategy", "phased")
    cm       = params.get("cm_support", "basic")
    horizon  = int(params.get("horizon_days", 90))
    size     = int(params.get("workforce_size", 1240))
    resist   = float(params.get("resist_baseline", 35))
    train    = float(params.get("train_effectiveness", 60))

    tb = TOOL_BOOST.get(tool, 0)
    sb = STRAT_BOOST.get(strategy, 0)
    cb = CM_BOOST.get(cm, 0)

    base = 55 + tb + sb + cb + train * 0.2 - resist * 0.3
    final_adoption = round(max(20, min(97, base + random.uniform(-2, 2))))

    # S-curve over horizon (weekly points)
    weeks = horizon // 7
    adoption_curve = []
    for i in range(weeks + 1):
        t = i / weeks
        val = final_adoption * (1 - math.exp(-4 * t)) / (1 - math.exp(-4))
        adoption_curve.append(round(max(3, min(final_adoption, val + random.uniform(-2, 2)))))
    adoption_curve[-1] = final_adoption

    # Productivity delta (weekly, dip then rise)
    prod_delta = []
    peak_impact = round((final_adoption - 55) * 0.4)
    for i in range(weeks):
        t = i / weeks
        dip = -8 * (1 - t) * (1 if strategy == "big_bang" else 0.5)
        growth = peak_impact * t
        prod_delta.append(round(dip + growth + random.uniform(-1, 1)))

    # Per-persona adoption
    persona_results = []
    for p in PERSONAS:
        pa = round(final_adoption * (p["adoption_speed"] / 100) * (1 - p["resistance"] / 200))
        pa = max(10, min(99, pa))
        persona_results.append({"id": p["id"], "adoption": pa})

    time_to_80 = None
    for i, v in enumerate(adoption_curve):
        if v >= 80:
            time_to_80 = i * 7
            break

    risk_score = round(
        max(5, min(90, 100 - final_adoption + resist * 0.3 - cb * 0.2 + random.uniform(-3, 3)))
    )
    risk = "LOW" if risk_score < 30 else "MEDIUM" if risk_score < 55 else "HIGH"

    # Collaboration impact
    collab = {
        "messaging":    round((final_adoption - 50) * 0.35),
        "meetings":     round((final_adoption - 55) * 0.2),
        "co_authoring": round((final_adoption - 48) * 0.45),
        "it_tickets":   round(-(final_adoption - 50) * 0.6),
    }

    return {
        "final_adoption":  final_adoption,
        "adoption_curve":  adoption_curve,
        "productivity_delta": prod_delta,
        "persona_results": persona_results,
        "time_to_80":      time_to_80,
        "risk_score":      risk_score,
        "risk":            risk,
        "collab_impact":   collab,
        "peak_prod_impact": peak_impact,
    }


# ─── ROUTES ───────────────────────────────────────────────────────────────────

@simulate_bp.get("/")
@login_required
def list_simulations():
    user = request.current_user
    q = Simulation.query if user.role == "admin" else Simulation.query.filter_by(user_id=user.id)
    sims = q.order_by(Simulation.created_at.desc()).all()
    return jsonify([s.to_dict() for s in sims])


@simulate_bp.post("/run")
@roles_required("admin", "analyst")   # viewers cannot run simulations
def run_simulation():
    user = request.current_user
    data = request.get_json(silent=True) or {}

    sim = Simulation(
        user_id          = user.id,
        name             = data.get("name") or f"Scenario #{Simulation.query.count()+1}",
        tool_change      = data.get("tool_change", "teams"),
        rollout_strategy = data.get("rollout_strategy", "phased"),
        cm_support       = data.get("cm_support", "basic"),
        horizon_days     = int(data.get("horizon_days", 90)),
        workforce_size   = int(data.get("workforce_size", 1240)),
        resist_baseline  = float(data.get("resist_baseline", 35)),
        train_effectiveness = float(data.get("train_effectiveness", 60)),
        status           = "running",
    )
    db.session.add(sim)
    db.session.commit()

    try:
        result = run_abm(data)
        sim.result_json = json.dumps(result)
        sim.status = "completed"
    except Exception as e:
        sim.status = "failed"
        db.session.commit()
        return jsonify({"error": str(e)}), 500

    db.session.commit()
    return jsonify({"simulation": sim.to_dict()}), 201


@simulate_bp.get("/<int:sim_id>")
@login_required
def get_simulation(sim_id):
    user = request.current_user
    sim  = Simulation.query.get_or_404(sim_id)
    if user.role != "admin" and sim.user_id != user.id:
        return jsonify({"error": "Access denied"}), 403
    return jsonify(sim.to_dict())


@simulate_bp.delete("/<int:sim_id>")
@roles_required("admin", "analyst")
def delete_simulation(sim_id):
    user = request.current_user
    sim  = Simulation.query.get_or_404(sim_id)
    if user.role != "admin" and sim.user_id != user.id:
        return jsonify({"error": "Access denied"}), 403
    db.session.delete(sim)
    db.session.commit()
    return jsonify({"message": "Deleted"})
