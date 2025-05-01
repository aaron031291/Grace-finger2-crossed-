
	3.	Login
	•	Username: admin
	•	Password: grace2025

⸻

What You’re Looking At

This dashboard is a glass brain for Grace:
	•	Live Cognitive Map: Real-time node graph of internal processes
	•	System Health Panel: Dynamic KPI diagnostics and status traces
	•	Command Console: Trigger audits, rollback modules, or inject new commands
	•	Theme + Layout Engine: Full CSS/graph layout powered by FastAPI endpoints
	•	Config System: Live theme, panel, and interaction overrides via display_config.py
	•	Breakpoints: Adaptive layout scaling across desktop, tablet, and mobile

⸻

Directory Structure
grace_core_systems/
├── GUI/
│   ├── dashboard/              # Full backend API logic (FastAPI)
│   ├── frontend/               # HTML/CSS/JS client
│   ├── backend.py              # Entry point for FastAPI
│   ├── display_config.py       # Theme, layout, and panel config (Pydantic)
│   ├── interface_router.py     # /api/interface/* routes
│   ├── layout_controller.py    # /api/layout/* endpoints
│   └── deployment/             # docker-compose, env, run-system.sh
├── static/                     # Static assets served at /static



⸻

Core Concepts
	•	Edge-native ready: Grace can run in containers, edge servers, or future nodes
	•	Memory-integrated: Data from modules and logs can write back into config
	•	Ethical-first architecture: All decisions are auditable, traceable, explainable
	•	Self-adaptive UI: Panel visibility, layout, and styling react to runtime config

⸻

Want to Extend Grace?
	•	Add new panels via display_config.panels
	•	Add commands to CommandExecution validator
	•	Add custom layout presets in GraphLayoutPreset
	•	Inject frontend logic via frontend/index.html
	•	Integrate new data streams into /ws/cognitive-map WebSocket endpoint

⸻

Deployment Notes

This system is currently development-mode only (running via Codespaces/local Docker). For production:
	•	Add HTTPS + domain config
	•	Use vaulted secrets instead of .env.example
	•	Secure WebSocket upgrade path (optional JWT gating)
	•	Connect real modules to Redis PubSub

⸻

License + Intent

Grace is not just a dashboard—it’s a self-evolving cognition engine. All contributions should honor the vision:

“Transparent, ethical, and sovereign intelligence—built in public, powered by truth.”
