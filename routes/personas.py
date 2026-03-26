from flask import Blueprint, jsonify
from auth_utils import login_required

personas_bp = Blueprint("personas", __name__)

PERSONAS = [
    {
        "id": "power", "icon": "🚀", "name": "Power User", "pct": 18, "color": "#00b4d8",
        "desc": "Tech-savvy early adopters. Drive organic adoption and act as internal champions.",
        "traits": {"Tool Adoption Speed": 92, "Collaboration Index": 85, "Resistance Level": 8,  "Training Need": 15}
    },
    {
        "id": "collab", "icon": "🤝", "name": "Collaborator", "pct": 24, "color": "#06d6a0",
        "desc": "Cross-functional connectors. High collaboration bandwidth, moderate tech comfort.",
        "traits": {"Tool Adoption Speed": 70, "Collaboration Index": 95, "Resistance Level": 20, "Training Need": 35}
    },
    {
        "id": "steady", "icon": "⚙️", "name": "Steady Operator", "pct": 29, "color": "#ffd166",
        "desc": "Process-oriented individuals. Prefer predictability, adopt with clear guidance.",
        "traits": {"Tool Adoption Speed": 55, "Collaboration Index": 60, "Resistance Level": 38, "Training Need": 55}
    },
    {
        "id": "resist", "icon": "🛡️", "name": "Change Resistant", "pct": 15, "color": "#f77f00",
        "desc": "Value established workflows. Require evidence and trust before adopting changes.",
        "traits": {"Tool Adoption Speed": 25, "Collaboration Index": 40, "Resistance Level": 75, "Training Need": 80}
    },
    {
        "id": "remote", "icon": "🌐", "name": "Remote-First", "pct": 14, "color": "#a78bfa",
        "desc": "Distributed workers. High digital dependency, adopt tools that improve async work.",
        "traits": {"Tool Adoption Speed": 78, "Collaboration Index": 72, "Resistance Level": 18, "Training Need": 28}
    },
]


@personas_bp.get("/")
@login_required
def list_personas():
    return jsonify(PERSONAS)


@personas_bp.get("/<persona_id>")
@login_required
def get_persona(persona_id):
    p = next((x for x in PERSONAS if x["id"] == persona_id), None)
    if not p:
        return jsonify({"error": "Persona not found"}), 404
    return jsonify(p)
