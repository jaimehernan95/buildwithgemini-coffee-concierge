# Google Cloud: Build with Gemini — Track 3 Complete Lab Architecture & Runbook 🚀

> **Workshop:** Build with Gemini · Track 3  
> **Objective:** Prototype, equip, evaluate, and deploy your own agent-first application on Google Cloud.  
> **Project:** Artisan Coffee Concierge (Multi-Agent System)

---

## 🧭 PART 1: Why Each Feature Was Asked & Its Architectural Benefits

Understanding the **"Why"** behind each component in Track 3:

### 1. Cross-Session Long-Term Memory (Vertex AI Memory Bank)
- **Why it was asked:** Standard LLM calls are stateless; as soon as a user session finishes or refreshes, the model forgets everything.
- **Architectural Benefit:** Memory Bank allows the agent to recall critical facts (such as customer dietary allergies, sensitivities, and favourite roast profiles) across completely different days or sessions. This prevents safety hazards (e.g., serving almond milk to someone allergic to tree nuts) and provides hyper-personalized concierge service without re-asking questions.

### 2. Audio (Speech-to-Text & Text-to-Speech)
- **Why it was asked:** Voice is the natural interface for kiosk, drive-thru, and mobile hospitality applications.
- **Architectural Benefit:** Allows hands-free operation and natural accessibility. It uses browser speech recognition and multilingual synthesis to allow instant real-time conversations in English, Spanish, Vietnamese, or Chinese.

### 3. Video / AI Persona Model & Dynamic Face Animation
- **Why it was asked:** Text chats feel impersonal. High-touch hospitality requires visual presence.
- **Architectural Benefit:** By pairing dynamic, high-fashion editorial AI portraits with real-time lip and voice wave animations, the application transforms a chatbot into an engaging, lifelike digital persona (Maya Vance / Leo Mercer) suitable for luxury brand experiences.

### 4. Continuous Re-deployment (Agent Engine & Cloud Run)
- **Why it was asked:** Real-world agent development is iterative. Whenever tools, database schemas, or subagent prompts change, the runtime must update with zero downtime.
- **Architectural Benefit:**
  - **Agent Engine (Vertex AI Reasoning Engines):** Manages serverless execution of the Python ADK agent, handles scaling, sandboxes, and telemetry.
  - **Cloud Run:** Hosts the stateless FastAPI web proxy and frontend, auto-scaling from 0 to 100+ instances based on traffic.

### 5. Multi-Agent Hierarchy
- **Why it was asked:** Monolithic single-prompt agents fail when overloaded with 10+ unrelated tools (hallucination, high token costs, and context confusion).
- **Architectural Benefit:** By splitting the system into specialized agents (`root_agent` Orchestrator, `nutrition_analyst_agent`, `order_logistics_agent`, `coffee_sommelier_agent`), each agent has a focused prompt and only the tools it needs, drastically improving reliability, accuracy, and execution speed.

### 6. Sandbox Python Execution & SQL Database Analytics
- **Why it was asked:** LLMs are notorious for making calculation errors when doing arithmetic or complex math.
- **Architectural Benefit:** Rather than guessing, the agent writes real Python code (`pandas`) or SQL queries executed in Vertex AI Sandbox Code Executor to compute exact statistics, ratios (e.g. caffeine-to-calorie metrics), and filters.

---

## 🛠️ PART 2: Step-by-Step Terminal Runbook (Exact Commands & Directories)

Follow this sequence to clone, set up, test, run, and deploy the application from scratch on any workstation.

---

### Phase 1: Environment Setup & Authentication

Navigate to your home/working folder:
```bash
# 1. Move to workspace root
cd ~/Desktop

# 2. Clone the repository
git clone https://github.com/jaimehernan95/buildwithgemini-coffee-concierge.git
cd buildwithgemini-coffee-concierge/coffee-concierge

# 3. Authenticate Google Cloud
gcloud auth login
gcloud auth application-default login

# 4. Set your target GCP Project ID
gcloud config set project <YOUR_PROJECT_ID>
```

---

### Phase 2: Python Environment & Dependency Installation

```bash
# Directory: buildwithgemini-coffee-concierge/coffee-concierge

# 1. Install astral uv (Fast Python toolchain)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# 2. Install Google Agents CLI tool
uv tool install google-agents-cli

# 3. Install project dependencies into virtual environment
agents-cli install
```

---

### Phase 3: Database Seeding & Setup

```bash
# Directory: buildwithgemini-coffee-concierge/coffee-concierge

# 1. Seed the local Starbucks beverage and macro SQLite database
python3 app/populate_starbucks_data.py

# 2. Seed the Firestore menu items catalog
python3 seed_firestore.py
```

---

### Phase 4: Run Automated Tests & Integration Benchmarks

Verify all tools, subagents, and memory persistence pass before running or deploying:
```bash
# Directory: buildwithgemini-coffee-concierge/coffee-concierge

# Set required environment variables for Vertex AI testing
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
export GOOGLE_CLOUD_LOCATION=us-central1

# Execute pytest on the multi-agent test suite
pytest tests/integration/test_agent.py tests/integration/test_multiagent_tools.py
```

---

### Phase 5: Local Testing & Playgrounds

#### Option A: Launch the ADK Agent Playground (Backend Dev UI)
```bash
# Directory: buildwithgemini-coffee-concierge/coffee-concierge
agents-cli playground
```
*Opens local ADK interactive testing interface at http://localhost:8000.*

#### Option B: Launch the Full Multilingual Voice & Video Chat Frontend
```bash
# Directory: buildwithgemini-coffee-concierge/coffee-concierge/frontend
cd frontend

# Run the FastAPI A2A Proxy and Web Server
python3 main.py
```
*Frontend runs locally on http://localhost:8080.*

---

### Phase 6: Cloud Deployment

#### 1. Deploy the Agent Engine (Reasoning Engine on Vertex AI)
```bash
# Directory: buildwithgemini-coffee-concierge/coffee-concierge
cd ~/Desktop/buildwithgemini-coffee-concierge/coffee-concierge

# Deploy agent to Agent Runtime
agents-cli deploy --project $(gcloud config get-value project)
```

#### 2. Deploy the Web Frontend to Cloud Run
```bash
# Directory: buildwithgemini-coffee-concierge/coffee-concierge/frontend
cd frontend

# Deploy containerized service to Cloud Run
gcloud run deploy coffee-concierge-frontend \
  --source . \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars="AGENT_DIRECTORY=app"
```

---

### Phase 7: Publish to GitHub & Claim Swag

```bash
# Directory: buildwithgemini-coffee-concierge
cd ~/Desktop/buildwithgemini-coffee-concierge

# Check status and push any new changes
git status
git add .
git commit -m "Update agent configuration"
git push origin main
```

---

## 📊 Summary of Implemented Architecture

| Layer | Technology | Role |
|---|---|---|
| **Orchestrator** | Google ADK `root_agent` | Persona, intent routing, A2UI layout formatting |
| **Subagents** | Nutritionist, Order Logistics, Sommelier | Focused task execution (math, maps, orders) |
| **Foundation Model** | `gemini-2.5-flash` | Reasoning, natural conversation, multilingual dialogue |
| **Visuals Model** | `gemini-3.1-flash-lite-image` | On-demand photorealistic latte & bakery generation |
| **Data & Macros** | SQLite + Python Pandas | Accurate arithmetic, nutritional rankings, and SQL queries |
| **Persistence** | Google Cloud Firestore | Session preservation, menu items, and customer orders |
| **Storage** | Google Cloud Storage | Public CDN for AI-generated beverage photos |
| **Frontend** | Vanilla JS + HTML5 + Web Speech API | Zero-dependency, lightweight, real-time voice & A2UI UI |
