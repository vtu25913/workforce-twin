from flask import Blueprint, jsonify, request
from auth_utils import login_required
from database import Simulation

insights_bp = Blueprint("insights", __name__)

PERSONA_NAMES = {
    "power": "Power User", "collab": "Collaborator",
    "steady": "Steady Operator", "resist": "Change Resistant", "remote": "Remote-First"
}


def _generate_insights(sim):
    r   = sim.result()
    if not r:
        return []

    adoption = r["final_adoption"]
    risk     = r["risk"]
    cm       = sim.cm_support
    strategy = sim.rollout_strategy

    recs = []

    recs.append({
        "type": "recommendation",
        "icon": "🎯",
        "title": "Deploy Change Champions",
        "body": "Power Users (18%) show 92% adoption speed. Activate them as internal ambassadors to create peer-driven adoption momentum.",
        "severity": "info",
    })

    if cm == "none":
        recs.append({
            "type": "risk",
            "icon": "🔴",
            "title": "Critical: No Change Management",
            "body": "Zero change management support will extend time-to-adoption by 40–60% and amplify resistance incidents. Add at minimum Basic support.",
            "severity": "high",
        })
    elif cm == "basic":
        recs.append({
            "type": "recommendation",
            "icon": "📋",
            "title": "Upgrade Change Management",
            "body": "Moving from Basic to Medium support (training sessions) would improve adoption by ~10–15% based on persona behavioral profiles.",
            "severity": "medium",
        })

    if strategy == "big_bang":
        recs.append({
            "type": "risk",
            "icon": "⚠️",
            "title": "Big Bang Rollout Amplifies Resistance",
            "body": "Phased deployment would increase adoption by ~12–18% by allowing personas to adjust gradually. Change Resistant (15%) are especially vulnerable.",
            "severity": "high",
        })

    recs.append({
        "type": "recommendation",
        "icon": "📅",
        "title": "Prepare for Week 3–5 Productivity Dip",
        "body": "Simulation predicts a temporary productivity trough during weeks 3–5. Pre-position IT surge support and reduce non-critical work during this window.",
        "severity": "medium",
    })

    if adoption < 60:
        recs.append({
            "type": "risk",
            "icon": "📉",
            "title": "Low Predicted Adoption",
            "body": f"Predicted adoption of {adoption}% is below the 70% viability threshold. Consider revising rollout strategy or increasing change management investment.",
            "severity": "high",
        })
    elif adoption >= 85:
        recs.append({
            "type": "recommendation",
            "icon": "✅",
            "title": "Strong Adoption Signal",
            "body": f"Predicted adoption of {adoption}% exceeds best-practice benchmarks. Proceed with confidence; monitor Change Resistant segment closely.",
            "severity": "low",
        })

    recs.append({
        "type": "risk",
        "icon": "🛡️",
        "title": "Change Resistant Concentration Risk",
        "body": "15% Change Resistant personas may form resistance coalitions in high-density departments. Map their distribution and deploy targeted coaching.",
        "severity": "medium",
    })

    return recs


@insights_bp.get("/<int:sim_id>")
@login_required
def get_insights(sim_id):
    user = request.current_user
    sim  = Simulation.query.get_or_404(sim_id)
    if user.role != "admin" and sim.user_id != user.id:
        return jsonify({"error": "Access denied"}), 403
    if sim.status != "completed":
        return jsonify({"error": "Simulation not completed yet"}), 400
    return jsonify({
        "simulation_id": sim_id,
        "insights": _generate_insights(sim)
    })
