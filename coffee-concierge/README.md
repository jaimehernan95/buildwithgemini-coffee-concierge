# Coffee Concierge ☕

An intelligent specialty coffee concierge AI agent built with the Google Agent Development Kit (ADK) and Gemini 2.5 Flash on Google Cloud. The agent helps customers explore artisan coffee menus, verifies dietary allergies, creates custom drink visuals on demand, tracks orders, finds nearby cafes, performs Starbucks nutrition analysis using Python/SQL, and coordinates across a multi-agent team.

![Coffee Concierge Demo](./demo.gif)

---

## 🌟 What This Agent Does

The agent acts as an artisan barista and coffee specialist with real, working integrations across Google Cloud and public APIs:

- **Hierarchical Multi-Agent Team**: An orchestrator agent (`root_agent`) delegating to specialized sub-agents:
  - 🥗 `nutrition_analyst_agent`: Performs SQL and Python pandas analytics on drinks, calories, and caffeine macros.
  - 📦 `order_logistics_agent`: Manages Firestore orders, tracking, and Google Places geocoding.
  - ☕ `coffee_sommelier_agent`: Looks up authentic brewing guides, origins, and live international currency conversion.
- **Browse Menu & Pricing**: Queries specialty coffee and bakery items with category filters (`espresso`, `cold_brew`, `pourover`, `bakery`) directly from Google Cloud Firestore.
- **Dietary & Allergen Memory**: Utilizes Vertex AI Memory Bank (`load_memory`) to retrieve and retain user allergies, sensitivities, and roast preferences across conversational sessions, ensuring safe recommendations.
- **On-Demand Specialty Drink Visuals**: Generates high-quality photorealistic drink and pastry photography via `gemini-3.1-flash-lite-image` on Vertex AI and automatically uploads generated assets to Google Cloud Storage.
- **Interactive UI (A2UI)**: Returns structured A2UI component schemas (cards, imagery, columns, and action buttons) for rich rendering in the chat interface.
- **Starbucks Nutritional & Macro Analytics**: Directly queries an in-memory Starbucks database using SQL (`query_coffee_analytics_db`) and executes Pandas scripts (`execute_coffee_python_analysis`).
- **Distributed Session Persistence**: Backs conversation state and chat histories in Google Cloud Firestore (`session_persistence.py`) for enterprise reliability.
- **Order Placement & Tracking**: Creates unique customer orders written into Firestore (`orders` collection) and checks live fulfillment status.
- **Local Cafe Discovery & Geocoding**: Geocodes customer addresses and performs radius searches for nearby cafes and bakeries using the Google Places API.
- **Live Currency Conversion**: Converts USD menu prices to global currencies (EUR, GBP, JPY, CAD, AUD, etc.) with real-time exchange rates.

---

## 🛠️ Implemented Tools & Google Cloud Services

Based on `app/agent.py` and `agents-cli-manifest.yaml`:

| Service / Tool | Implementation | Description |
|---|---|---|
| **Gemini 2.5 Flash** | `google.adk.models.Gemini` | Primary conversational reasoning model. |
| **Hierarchical Multi-Agent** | `sub_agents=[...]` in ADK | Dedicated agents for Nutrition, Logistics, and Coffee Sommelier. |
| **Vertex AI Memory Bank** | `google.adk.tools.load_memory` | Cross-session memory for customer allergies, dietary preferences, and taste profiles. |
| **Google Cloud Firestore** | `google.cloud.firestore` | Document database for live `menu_items` catalog, `orders`, and distributed `agent_sessions`. |
| **Google Cloud Storage** | `google.cloud.storage` | Storage bucket hosting generated beverage and bakery images with public CDN URLs. |
| **Vertex AI Image Generation** | `gemini-3.1-flash-lite-image` | On-demand specialty beverage photography via Vertex AI (`generate_item_image`). |
| **Python Data Analytics** | `pandas` + `sqlite3` | In-memory execution of custom analytics code (`execute_coffee_python_analysis`). |
| **SQL Beverage Analytics DB** | `starbucks_analytics.db` | Curated database of Starbucks beverage macros, sizes, and caffeine metrics. |
| **A2UI Protocol** | `A2uiSchemaManager` + `a2ui_callback` | Emits structured display cards, tables, and media components in responses. |
| **Google Maps & Places APIs** | `geocode_address` + `find_nearby_places` | Geocoding and geographic search for nearby coffee establishments. |
| **Currency Exchange API** | `convert_currency` | Live FX rates for international menu pricing. |
| **Coffee Guide API** | `lookup_coffee_guide` | Reference database for coffee beverage history, ingredients, and recipes. |

---

## 🚀 Step-by-Step Setup & Build Instructions

### Step 1: Clone the Repository
```bash
git clone https://github.com/jaimehernan95/buildwithgemini-coffee-concierge.git
cd buildwithgemini-coffee-concierge/coffee-concierge
```

### Step 2: Set Up Python Environment & Google Cloud SDK
Ensure Python 3.11+ and the Google Cloud SDK are installed and authenticated:
```bash
# Authenticate Google Cloud
gcloud auth login
gcloud auth application-default login
gcloud config set project <YOUR_GCP_PROJECT_ID>

# Install uv package manager (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 3: Install Project Dependencies
Install the required packages using `uv` or `agents-cli`:
```bash
uv tool install google-agents-cli
agents-cli install
```

### Step 4: Populate the Coffee Analytics & Firestore Databases
Seed the initial database files:
```bash
python3 app/populate_starbucks_data.py
python3 seed_firestore.py
```

### Step 5: Run Automated Integration Tests & Audits
Run the full test suite to verify tool-calling, multi-agent hierarchy, and session persistence:
```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=<YOUR_GCP_PROJECT_ID>
export GOOGLE_CLOUD_LOCATION=us-central1

pytest tests/integration/test_agent.py tests/integration/test_multiagent_tools.py
```

### Step 6: Run Locally
- **Option A: Test the Agent Backend with ADK Playground**
  ```bash
  agents-cli playground
  ```
- **Option B: Run the Full Multilingual Voice & A2UI Chat Frontend**
  ```bash
  cd frontend
  python3 main.py
  ```

### Step 7: Deploy to Google Cloud (Optional)
- **Deploy Agent to Agent Engine:**
  ```bash
  agents-cli deploy --project <YOUR_GCP_PROJECT_ID>
  ```
- **Deploy Frontend to Cloud Run:**
  ```bash
  cd frontend
  gcloud run deploy coffee-concierge-frontend \
    --source . \
    --region us-east1 \
    --allow-unauthenticated
  ```

---

## 📁 Repository Structure

```
.
├── coffee-concierge/
│   ├── app/
│   │   ├── agent.py               # Hierarchical multi-agent team and tool definitions
│   │   ├── a2ui_utils.py          # A2UI schema manager and response callbacks
│   │   ├── session_persistence.py # Distributed Firestore session persistence
│   │   ├── starbucks_analytics.db # SQLite database with Starbucks drinks & nutrition data
│   │   ├── populate_starbucks_data.py # Database seeder script
│   │   └── fast_api_app.py        # FastAPI server entrypoint
│   ├── frontend/
│   │   ├── main.py                # FastAPI proxy connecting to Agent Engine over A2A
│   │   └── static/
│   │       ├── index.html         # Multilingual chat UI, voice synthesis & STT, AI persona avatars
│   │       └── ...                # Static media assets and high-fashion model portraits
│   ├── tests/
│   │   └── integration/
│   │       ├── test_agent.py          # E2E agent streaming test
│   │       └── test_multiagent_tools.py # Multi-agent tool benchmark test suite
│   ├── agents-cli-manifest.yaml   # ADK agent deployment manifest (A2A protocol enabled)
│   └── pyproject.toml             # Project dependencies and configuration
├── demo.gif                       # Optimized looping demo recording
└── README.md                      # Project documentation and build guide
```
