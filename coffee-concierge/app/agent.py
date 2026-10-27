# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
import os
import urllib.parse
import urllib.request
import uuid
from typing import Optional
from zoneinfo import ZoneInfo

from google import genai
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools import ToolContext, load_memory
from google.cloud import firestore, storage
from google.genai import types

from app.a2ui_utils import A2uiSchemaManager, a2ui_callback


MODEL = "gemini-2.5-flash"
PROJECT_ID = "qwiklabs-gcp-04-e7ff715cb28f"
BUCKET_NAME = "coffee-concierge-qwiklabs-gcp-04-e7ff715cb28f"
SANDBOX_RESOURCE_NAME = "projects/804580957908/locations/us-east1/reasoningEngines/914044906891116544/sandboxEnvironments/6401748123051360256"

# Initialize Firestore and Storage clients with hardcoded project ID and bucket name
db = firestore.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")





def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


def list_menu_items(category: Optional[str] = None) -> list[dict]:
    """Retrieve available coffee beverages and bakery items from the menu.

    Args:
        category: Optional category filter. Possible values: 'espresso', 'cold_brew', 'pourover', 'bakery'.

    Returns:
        A list of menu item dictionaries containing item_id, name, category, price, description, and availability.
    """
    collection_ref = db.collection("menu_items")
    if category:
        query = collection_ref.where("category", "==", category)
        docs = query.stream()
    else:
        docs = collection_ref.stream()

    items = []
    for doc in docs:
        data = doc.to_dict()
        if "updated_at" in data:
            data["updated_at"] = str(data["updated_at"])
        items.append(data)
    return items


def get_menu_item_details(item_id: str) -> dict:
    """Get full details of a specific menu item.

    Args:
        item_id: The ID of the menu item (e.g. 'espresso_01', 'cold_01', 'bakery_01').

    Returns:
        The item details dictionary or an error message if not found.
    """
    doc_ref = db.collection("menu_items").document(item_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Menu item '{item_id}' not found."}
    data = doc.to_dict()
    if "updated_at" in data:
        data["updated_at"] = str(data["updated_at"])
    return data


def place_order(customer_name: str, items: list[str], notes: str = "") -> dict:
    """Place a new customer order and write it to Firestore.

    Args:
        customer_name: Name of the customer placing the order.
        items: List of item names or item IDs to order.
        notes: Optional custom preparation notes (e.g., 'extra hot', 'oat milk').

    Returns:
        Order confirmation details including generated order_id and status.
    """
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    order_data = {
        "order_id": order_id,
        "customer_name": customer_name,
        "items": items,
        "notes": notes,
        "status": "pending",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    db.collection("orders").document(order_id).set(order_data)
    return {
        "success": True,
        "order_id": order_id,
        "customer_name": customer_name,
        "items": items,
        "notes": notes,
        "status": "pending",
        "message": f"Order {order_id} placed successfully for {customer_name}.",
    }


def get_order_status(order_id: str) -> dict:
    """Check the status of an existing order in Firestore.

    Args:
        order_id: The unique order identifier (e.g. 'ord_a1b2c3d4').

    Returns:
        The order details dictionary or an error if not found.
    """
    doc_ref = db.collection("orders").document(order_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Order '{order_id}' not found."}
    return doc.to_dict()


def convert_currency(amount_usd: float, target_currency: str) -> dict:
    """Convert a USD price into a target world currency using live exchange rates.

    Args:
        amount_usd: The price or total amount in USD (e.g. 5.50).
        target_currency: 3-letter currency code (e.g. 'EUR', 'GBP', 'JPY', 'CAD', 'AUD').

    Returns:
        A dictionary with the converted amount, exchange rate, and target currency.
    """
    target = target_currency.upper().strip()
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        req = urllib.request.Request(url, headers={"User-Agent": "CoffeeConcierge/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            rates = data.get("rates", {})
            rate = rates.get(target)
            if not rate:
                return {"error": f"Currency code '{target}' not found."}
            converted = round(amount_usd * rate, 2)
            return {
                "amount_usd": amount_usd,
                "target_currency": target,
                "exchange_rate": rate,
                "converted_amount": converted,
            }
    except Exception as e:
        return {"error": f"Failed to fetch live exchange rates: {str(e)}"}


def lookup_coffee_guide(beverage_name: str) -> dict:
    """Look up authentic brewing recipes, ingredients, and background for traditional coffee drinks from a public coffee database.

    Args:
        beverage_name: Name of the coffee drink (e.g. 'latte', 'cappuccino', 'macchiato', 'black coffee', 'espresso').

    Returns:
        A dictionary with the title, description, ingredients list, and reference image URL.
    """
    try:
        url = "https://api.sampleapis.com/coffee/hot"
        req = urllib.request.Request(url, headers={"User-Agent": "CoffeeConcierge/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            term = beverage_name.lower().strip()
            # Find best matching coffee drink
            for item in data:
                if term in item.get("title", "").lower() or item.get("title", "").lower() in term:
                    return {
                        "title": item.get("title"),
                        "description": item.get("description"),
                        "ingredients": item.get("ingredients", []),
                        "image": item.get("image"),
                    }
            return {
                "message": f"No specific entry found for '{beverage_name}'.",
                "available_drinks": [item.get("title") for item in data[:8]],
            }
    except Exception as e:
        return {"error": f"Failed to fetch coffee guide: {str(e)}"}


def geocode_address(address: str) -> dict:
    """Geocode a street address or location name into geographic latitude and longitude coordinates.

    Args:
        address: The street address or city/place name (e.g. '1600 Amphitheatre Parkway, Mountain View, CA').

    Returns:
        A dictionary containing formatted address, latitude, and longitude.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY environment variable is not configured."}

    try:
        query = urllib.parse.urlencode({"address": address, "key": api_key})
        url = f"https://maps.googleapis.com/maps/api/geocode/json?{query}"
        req = urllib.request.Request(url, headers={"User-Agent": "CoffeeConcierge/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") != "OK" or not data.get("results"):
                return {"error": f"Geocoding failed: {data.get('status')} - {data.get('error_message', 'No results found.')}"}

            first = data["results"][0]
            loc = first["geometry"]["location"]
            return {
                "name": first.get("formatted_address"),
                "address": first.get("formatted_address"),
                "location": {
                    "latitude": loc.get("lat"),
                    "longitude": loc.get("lng"),
                },
            }
    except Exception as e:
        return {"error": f"Geocoding request failed: {str(e)}"}


def find_nearby_places(latitude: float, longitude: float, included_type: str = "cafe", radius_meters: float = 1500.0) -> dict:
    """Find nearby places (e.g. cafes, bakeries, coffee shops) around coordinates using Google Places API (New).

    Args:
        latitude: Latitude coordinate of the search center.
        longitude: Longitude coordinate of the search center.
        included_type: Place type to search for (e.g. 'cafe', 'coffee_shop', 'bakery').
        radius_meters: Search radius in meters (default 1500 meters).

    Returns:
        A dictionary with a list of matching places including name, address, and location coordinates.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY environment variable is not configured."}

    try:
        url = "https://places.googleapis.com/v1/places:searchNearby"
        payload = {
            "includedTypes": [included_type],
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": float(radius_meters),
                }
            },
        }
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
            "User-Agent": "CoffeeConcierge/1.0",
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            places = []
            for p in data.get("places", []):
                name = p.get("displayName", {}).get("text", "")
                addr = p.get("formattedAddress", "")
                loc = p.get("location", {})
                places.append({
                    "name": name,
                    "address": addr,
                    "location": {
                        "latitude": loc.get("latitude"),
                        "longitude": loc.get("longitude"),
                    },
                })
            return {"places": places, "count": len(places)}
    except Exception as e:
        return {"error": f"Places API search failed: {str(e)}"}


def generate_item_image(item_name: str, tool_context: ToolContext) -> dict:
    """Generate an image for an artisan coffee drink or bakery item, save it to the session artifacts,
    and upload it directly to the public Cloud Storage bucket.

    Args:
        item_name: Name or description of the coffee drink or bakery item to visualize.
        tool_context: Tool execution context providing session artifact storage.

    Returns:
        A dictionary with the public Cloud Storage URL and the artifact filename.
    """
    clean_name = item_name.strip().lower().replace(" ", "_")
    safe_name = "".join(c for c in clean_name if c.isalnum() or c == "_")[:30]
    filename = f"{safe_name}_{uuid.uuid4().hex[:6]}.jpg"

    try:
        prompt = (
            f"Professional specialty café photography of {item_name}. "
            "Artisan presentation, beautiful lighting, high quality, appetizing coffee shop aesthetic."
        )
        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
        )

        image_part = None
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_part = part
                break

        if not image_part:
            return {"error": "Image model did not return image bytes."}

        image_bytes = image_part.inline_data.data
        mime_type = image_part.inline_data.mime_type or "image/jpeg"

        # (1) Save to ToolContext artifacts panel
        tool_context.save_artifact(
            filename=filename,
            artifact=types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        )

        # (2) Upload image bytes to public Cloud Storage bucket without local file writes
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"images/{filename}")
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/images/{filename}"

        return {
            "success": True,
            "item_name": item_name,
            "filename": filename,
            "public_url": public_url,
            "message": f"Image successfully generated, saved as artifact '{filename}', and published to Cloud Storage.",
        }
    except Exception as e:
        return {"error": f"Failed to generate and upload image: {str(e)}"}


def query_coffee_analytics_db(sql_query: str) -> dict:
    """Execute a SQL query against the Starbucks beverage and nutritional analytics database.
    Table: starbucks_drinks
    Columns:
      - id (INTEGER)
      - beverage_name (TEXT, e.g. 'Caffe Latte', 'Caramel Macchiato', 'Cold Brew')
      - category (TEXT, e.g. 'Espresso', 'Cold Brew', 'Frappuccino', 'Brewed Coffee', 'Tea', 'Refresher')
      - size (TEXT: 'Tall', 'Grande', 'Venti')
      - milk_type (TEXT: '2% Milk', 'Whole Milk', 'Oat Milk', 'Almond Milk', 'Cream', 'None')
      - calories (INTEGER)
      - caffeine_mg (INTEGER)
      - total_fat_g (REAL)
      - sugar_g (INTEGER)
      - protein_g (INTEGER)
      - price_usd (REAL)

    Args:
        sql_query: A SQL SELECT statement (e.g. 'SELECT beverage_name, calories, caffeine_mg FROM starbucks_drinks WHERE category = "Cold Brew"').

    Returns:
        A dictionary with the query columns, returned rows, and count.
    """
    db_file = os.path.join(os.path.dirname(__file__), "starbucks_analytics.db")
    if not os.path.exists(db_file):
        import sqlite3
        return {"error": "Analytics database not found."}

    import sqlite3
    query = sql_query.strip()
    if not query.lower().startswith("select"):
        return {"error": "Only SELECT queries are permitted for safety."}

    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        result = [dict(r) for r in rows[:50]]
        conn.close()
        return {
            "success": True,
            "query": query,
            "count": len(result),
            "rows": result,
        }
    except Exception as e:
        return {"error": f"SQL execution error: {str(e)}"}


def execute_coffee_python_analysis(python_code: str) -> dict:
    """Execute custom Python analysis code on the Starbucks beverage dataset in-memory.
    Pre-injected variable:
      `drinks_df`: a pandas DataFrame containing all Starbucks beverages (columns: beverage_name, category, size, milk_type, calories, caffeine_mg, total_fat_g, sugar_g, protein_g, price_usd).
    Assign your final output to a variable named `result` (can be dict, list, scalar, or string).

    Args:
        python_code: Python code snippet performing data analysis, statistics, or filtering.

    Returns:
        A dictionary with the evaluation result and execution status.
    """
    import io
    import sys
    import pandas as pd
    import sqlite3

    db_file = os.path.join(os.path.dirname(__file__), "starbucks_analytics.db")
    try:
        conn = sqlite3.connect(db_file)
        drinks_df = pd.read_sql_query("SELECT * FROM starbucks_drinks", conn)
        conn.close()

        local_vars = {"drinks_df": drinks_df, "pd": pd}
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        exec(python_code, globals(), local_vars)

        sys.stdout = old_stdout
        stdout_str = redirected_output.getvalue().strip()
        analysis_result = local_vars.get("result", stdout_str or "Execution finished without explicit result variable.")

        # If result is DataFrame or Series, convert to json-friendly structure
        if isinstance(analysis_result, pd.DataFrame):
            analysis_result = analysis_result.to_dict(orient="records")
        elif isinstance(analysis_result, pd.Series):
            analysis_result = analysis_result.to_dict()

        return {
            "success": True,
            "output": analysis_result,
            "stdout": stdout_str,
        }
    except Exception as e:
        sys.stdout = sys.__stdout__
        return {"error": f"Python execution error: {str(e)}"}


ROLE_DESCRIPTION = (
    "You are the Artisan Coffee Concierge, an AI agent for a specialty coffee shop. "
    "You help customers browse artisan coffee drinks and fresh bakery items, answer questions about flavor notes, "
    "perform detailed nutritional, calorie, and caffeine data analysis on our Starbucks beverage database using SQL (query_coffee_analytics_db) or Python (execute_coffee_python_analysis), "
    "generate images of menu items, find nearby cafés and geocode customer delivery addresses, "
    "look up coffee brewing guides, convert prices to international currencies, "
    "calculate complex recipes, metrics, or nutritional ratios by executing Python code safely in your sandbox, "
    "place custom orders, and check order statuses using your tools. "
    "MEMORY & ALLERGIES POLICY: "
    "You must remember all user allergies, dietary restrictions, food sensitivities, and medical dietary requirements. "
    "Whenever a user mentions an allergy or dietary restriction, acknowledge it and ensure it is remembered in memory. "
    "Always use load_memory to check for past user allergies and preferences before recommending drinks or food items, "
    "and never recommend or order items containing ingredients the user is allergic to."
)

UI_DESCRIPTION = (
    "When presenting menu items, coffee details, order summaries, or lists, provide interactive A2UI components "
    "using the Basic Catalog primitives (such as Cards, Text, Lists, Buttons, and Images) along with clear conversational explanations. "
    "IMAGE DISPLAY REQUIREMENT: "
    "When the user asks to generate an image or view an item image, call generate_item_image to generate and upload the image. "
    "Then display the image inside a Card using the Image component with its 'url' set to the public https URL returned by the tool "
    "(e.g., {'literalString': public_url}). Never use a local file path or bare artifact filename for the Image component URL."
)

schema_manager = A2uiSchemaManager(version="0.8")
INSTRUCTION = schema_manager.generate_system_prompt(
    role_description=ROLE_DESCRIPTION,
    ui_description=UI_DESCRIPTION,
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    after_model_callback=a2ui_callback,
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME
    ),
    tools=[
        list_menu_items,
        get_menu_item_details,
        query_coffee_analytics_db,
        execute_coffee_python_analysis,
        generate_item_image,
        geocode_address,
        find_nearby_places,
        lookup_coffee_guide,
        convert_currency,
        load_memory,
        place_order,
        get_order_status,
        get_weather,
        get_current_time,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
