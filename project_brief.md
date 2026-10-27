# Project Brief: Artisan Coffee Concierge (coffee-concierge)

## 1. Project Overview
- **Project Name:** `coffee-concierge`
- **Model:** Gemini 3.8 Flash (`gemini-3.8-flash`)
- **Description:** An autonomous AI concierge for an artisan café. The agent assists guests in exploring specialized coffee brews, espresso drinks, and pastry pairings, retrieving real-time menu details, recommendations, and placing custom orders.

## 2. Backend & Data Architecture
- **Database:** Google Cloud Firestore (Native mode)
- **GCP Project ID:** `qwiklabs-gcp-04-e7ff715cb28f`
- **Primary Collection:** `menu_items`
  - `item_id` (string): Unique identifier (e.g., `item_espresso_01`)
  - `name` (string): Display name (e.g., "Vanilla Oat Flat White")
  - `category` (string): `espresso`, `cold_brew`, `pourover`, `bakery`
  - `price` (number): Price in USD (e.g., 5.50)
  - `description` (string): Flavor notes, roast profile, origin details
  - `image_url` (string): Public Cloud Storage URL for item photography
  - `available` (boolean): Inventory status
- **Secondary Collection:** `orders`
  - `order_id` (string): Unique order reference
  - `customer_name` (string): Customer name
  - `items` (list of strings): Selected item IDs or names
  - `total_price` (number): Order total
  - `status` (string): `pending`, `preparing`, `completed`
  - `created_at` (timestamp): Order creation timestamp

## 3. Storage Architecture
- **Cloud Storage Bucket:** Publicly accessible asset bucket for item images
- **Access Policy:** Public read (`allUsers:roles/storage.objectViewer`) for embedding images into web interfaces and client cards.

## 4. Agent Function Tools
1. `list_menu_items(category: str = None)`: Queries the `menu_items` Firestore collection for available products.
2. `get_item_details(item_name_or_id: str)`: Fetches complete taste profiles, allergens, origin, and image URL.
3. `place_order(customer_name: str, items: list[str], notes: str = "")`: Saves a new order record into the `orders` Firestore collection.
4. `check_order_status(order_id: str)`: Looks up real-time status of an active customer order.
