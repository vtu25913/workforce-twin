# 🔮 WorkforceTwin — Digital Twin Intelligence Platform

A **full-stack web application** that builds a **digital twin of your workforce** — simulating how employees respond to organisational change *before* it happens. Built with Python (Flask), synthetic datasets, and a premium web dashboard.

🔗 **Live App**: [https://workforce-twin-production.up.railway.app/](https://workforce-twin-production.up.railway.app/)
📂 **GitHub Repo**: [https://github.com/Yamini-Bathini/workforce-twin](https://github.com/Yamini-Bathini/workforce-twin)

---

## 🚀 Features

* 🔐 **Authentication & Role-Based Access**
  * JWT-based login, registration, and session management
  * Three roles: **Admin**, **Analyst**, **Viewer**
  * New registrations default to Viewer — only Admin can promote

* 📊 **Workforce Intelligence Dashboard**
  * KPI cards, telemetry charts, behavioural cluster visualisations
  * Real-time simulation summary and recent activity feed

* 🧩 **Synthetic Workforce Personas**
  * 5 ML-clustered behavioural archetypes (Power User, Collaborator, Steady Operator, Change Resistant, Remote-First)
  * Privacy-first: zero individual tracking, k-anonymity enforced (k≥15)

* ⚡ **Agent-Based Simulation Engine**
  * Configure change scenarios: tool rollout, hybrid work policy, team restructuring, and more
  * 1,240 synthetic agents · S-curve adoption modelling · risk scoring
  * Per-persona adoption breakdown, productivity delta, collaboration impact

* 📋 **Simulation History & Results**
  * Full history of all scenario runs per user
  * Adoption curve charts, ROI risk gauge, AI-generated insights

* ⚙️ **Admin Panel**
  * Full user management: create, enable/disable, change roles, delete
  * Platform-wide statistics: total users, active users, total simulations

* 🌐 **Responsive Web Interface**
  * Premium light-theme SPA served via Flask static files
  * Works on desktop and mobile

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, Flask, SQLAlchemy |
| **Auth** | JWT (PyJWT), Werkzeug password hashing |
| **Database** | PostgreSQL (production) / SQLite (local) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Deployment** | Railway, Gunicorn |

---

## 📂 Project Structure

```
workforce-twin/
├── app.py                 # Flask app factory + SPA routing
├── auth_utils.py          # JWT create/decode + decorators
├── database.py            # SQLAlchemy models + seed data
├── requirements.txt       # Python dependencies
├── Procfile               # Railway deployment config
├── runtime.txt            # Python version pin
├── routes/
│   ├── auth.py            # POST /api/auth/login|register|me|change-password
│   ├── dashboard.py       # GET  /api/dashboard/summary|telemetry|recent-simulations
│   ├── personas.py        # GET  /api/personas/
│   ├── simulate.py        # GET/POST/DELETE /api/simulate/ + ABM engine
│   ├── insights.py        # GET  /api/insights/<sim_id>
│   └── admin.py           # CRUD /api/admin/users + stats
└── static/
    └── index.html         # Full SPA frontend
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Yamini-Bathini/workforce-twin.git
cd workforce-twin
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```bash
python app.py
```

App available at: `http://127.0.0.1:8000/`

---

## 🧑‍💻 How to Use

1. **Open the Application**
   Visit the live app or run locally at `http://127.0.0.1:8000/`

2. **Sign In**
   Use the demo accounts below or register a new account (registered as Viewer by default)

3. **Explore the Dashboard**
   View workforce telemetry, behavioural clusters, KPIs and recent simulations

4. **Browse Personas**
   Explore the 5 synthetic workforce archetypes and their trait scores

5. **Run a Simulation**
   Configure a change scenario (tool, strategy, communication level, training) and run the agent-based model

6. **View Results**
   Analyse adoption curves, productivity impact, risk scores and AI-generated insights

7. **Admin Panel** *(Admin only)*
   Manage users, assign roles, view platform statistics

---

## 🔐 Demo Accounts

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Admin** | admin@twin.ai | Admin@123 | Everything + user management |
| **Analyst** | analyst@twin.ai | Analyst@123 | Run simulations + view results |
| **Viewer** | viewer@twin.ai | Viewer@123 | View results only (read-only) |

> 🔒 New user registrations default to **Viewer** role. Only an Admin can promote users to Analyst or Admin.

---

## 📡 API Reference

### Authentication
```
POST /api/auth/register        { name, email, password, org }
POST /api/auth/login           { email, password } → { token, user }
GET  /api/auth/me              → { user }
POST /api/auth/change-password { old_password, new_password }
```

### Dashboard
```
GET /api/dashboard/summary              → KPIs and last simulation summary
GET /api/dashboard/recent-simulations   → Last 10 simulations
GET /api/dashboard/telemetry            → 12-month tool usage data
```

### Simulation
```
POST   /api/simulate/run    { tool_change, rollout_strategy, cm_support,
                              horizon_days, workforce_size,
                              resist_baseline, train_effectiveness }
GET    /api/simulate/       → list of simulations
GET    /api/simulate/<id>   → single simulation with full result
DELETE /api/simulate/<id>   → delete simulation
```

### Admin *(admin role required)*
```
GET    /api/admin/users
POST   /api/admin/users          { name, email, role, org, password }
PATCH  /api/admin/users/<id>     { role?, is_active?, name?, org? }
DELETE /api/admin/users/<id>
GET    /api/admin/stats
```

---

## 🧠 How the Simulation Engine Works

Located in `routes/simulate.py → run_abm()`

1. **Inputs** — tool change type, rollout strategy, change management support, simulation horizon, workforce size, resistance baseline, training effectiveness
2. **Base adoption** — calculated from weighted inputs with per-tool and per-strategy boosts
3. **S-curve trajectory** — weekly adoption points over the simulation horizon
4. **Per-persona breakdown** — adoption rate per archetype based on behavioural traits
5. **Derived metrics** — productivity delta, collaboration impact, risk score (LOW / MEDIUM / HIGH)
6. **Output** — structured JSON stored in `Simulation.result_json`

---

## 🔒 Privacy Architecture

| Principle | Implementation |
|---|---|
| No individual tracking | All signals aggregated at cluster level |
| Zero PII stored | Synthetic personas only — never real employee profiles |
| K-anonymity | Every data point represents ≥15 individuals |
| Privacy by design | Simulation engine runs on synthetic data throughout |

---

## 🌍 Deployment

Deployed on **Railway** with PostgreSQL:

```
Procfile:     web: gunicorn app:flask_app --bind 0.0.0.0:$PORT
runtime.txt:  python-3.11.9
```

**Environment Variables:**
```
SECRET_KEY   = your-secret-key-here
DATABASE_URL = (auto-injected by Railway PostgreSQL)
PORT         = 8000
```

---

## 📌 Use Cases

* Workforce change management planning
* HR analytics and digital transformation strategy
* Scenario simulation before policy rollout
* Organisational risk assessment
* Data-driven leadership decisions

---

## 🔥 Extending the Platform

* **Real ML clustering** — Replace `PERSONAS` with scikit-learn K-means on real telemetry CSVs
* **Real ABM** — Replace `run_abm()` with the Mesa agent-based modelling framework
* **PostgreSQL** — Already configured via `DATABASE_URL` environment variable
* **Production hardening** — `DEBUG=False` is set automatically via Gunicorn