import datetime
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-e7ff715cb28f"

def seed():
    print(f"Connecting to Firestore for project {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    
    items = [
        {
            "item_id": "espresso_01",
            "name": "Vanilla Oat Flat White",
            "category": "espresso",
            "price": 5.50,
            "description": "Double espresso ristretto with micro-foamed oat milk and Madagascar bourbon vanilla.",
            "image_url": "https://storage.googleapis.com/coffee-concierge-assets/vanilla-flat-white.jpg",
            "available": True,
            "updated_at": datetime.datetime.now(datetime.timezone.utc),
        },
        {
            "item_id": "espresso_02",
            "name": "Classic Cortado",
            "category": "espresso",
            "price": 4.75,
            "description": "Equal parts espresso and steamed whole milk, cutting acidity with velvety texture.",
            "image_url": "https://storage.googleapis.com/coffee-concierge-assets/cortado.jpg",
            "available": True,
            "updated_at": datetime.datetime.now(datetime.timezone.utc),
        },
        {
            "item_id": "cold_01",
            "name": "Nitro Cold Brew",
            "category": "cold_brew",
            "price": 5.25,
            "description": "Slow-steeped single origin Ethiopian roast infused with nitrogen for a creamy stout-like head.",
            "image_url": "https://storage.googleapis.com/coffee-concierge-assets/nitro-cold-brew.jpg",
            "available": True,
            "updated_at": datetime.datetime.now(datetime.timezone.utc),
        },
        {
            "item_id": "pourover_01",
            "name": "Panama Geisha Pour-Over",
            "category": "pourover",
            "price": 8.00,
            "description": "Delicate and floral with notes of jasmine, bergamot, and ripe peach.",
            "image_url": "https://storage.googleapis.com/coffee-concierge-assets/geisha-pourover.jpg",
            "available": True,
            "updated_at": datetime.datetime.now(datetime.timezone.utc),
        },
        {
            "item_id": "bakery_01",
            "name": "Almond Croissant",
            "category": "bakery",
            "price": 4.50,
            "description": "Flaky buttery pastry filled with sweet almond frangipane and topped with sliced toasted almonds.",
            "image_url": "https://storage.googleapis.com/coffee-concierge-assets/almond-croissant.jpg",
            "available": True,
            "updated_at": datetime.datetime.now(datetime.timezone.utc),
        },
        {
            "item_id": "bakery_02",
            "name": "Cardamom Pistachio Morning Bun",
            "category": "bakery",
            "price": 4.75,
            "description": "Laminated dough swirled with freshly ground cardamom sugar and crushed pistachios.",
            "image_url": "https://storage.googleapis.com/coffee-concierge-assets/morning-bun.jpg",
            "available": True,
            "updated_at": datetime.datetime.now(datetime.timezone.utc),
        }
    ]

    collection_ref = db.collection("menu_items")
    for item in items:
        doc_ref = collection_ref.document(item["item_id"])
        doc_ref.set(item)
        print(f"Seeded menu item: {item['name']} ({item['item_id']})")

    print("Firestore seeding completed successfully!")

if __name__ == "__main__":
    seed()
