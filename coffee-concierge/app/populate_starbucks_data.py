import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "starbucks_analytics.db")

def create_and_seed_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("DROP TABLE IF EXISTS starbucks_drinks")
    cur.execute("""
    CREATE TABLE starbucks_drinks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        beverage_name TEXT NOT NULL,
        category TEXT NOT NULL,
        size TEXT NOT NULL,
        milk_type TEXT,
        calories INTEGER,
        caffeine_mg INTEGER,
        total_fat_g REAL,
        sugar_g INTEGER,
        protein_g INTEGER,
        price_usd REAL
    );
    """)

    # Curated real-world Starbucks nutritional & pricing sample dataset
    sample_drinks = [
        # Espresso / Lattes
        ("Caffe Latte", "Espresso", "Tall", "2% Milk", 150, 75, 6.0, 14, 10, 4.25),
        ("Caffe Latte", "Espresso", "Grande", "2% Milk", 190, 150, 7.0, 18, 12, 4.95),
        ("Caffe Latte", "Espresso", "Grande", "Oat Milk", 210, 150, 7.0, 14, 3, 5.75),
        ("Caffe Latte", "Espresso", "Grande", "Almond Milk", 130, 150, 6.0, 7, 3, 5.75),
        ("Caffe Latte", "Espresso", "Venti", "2% Milk", 250, 150, 9.0, 24, 15, 5.45),
        
        # Americano
        ("Caffe Americano", "Espresso", "Tall", "None", 10, 150, 0.0, 0, 1, 3.45),
        ("Caffe Americano", "Espresso", "Grande", "None", 15, 225, 0.0, 0, 1, 3.95),
        ("Caffe Americano", "Espresso", "Venti", "None", 25, 300, 0.0, 0, 2, 4.45),

        # Macchiatos
        ("Caramel Macchiato", "Espresso", "Tall", "2% Milk", 190, 75, 6.0, 25, 8, 4.95),
        ("Caramel Macchiato", "Espresso", "Grande", "2% Milk", 250, 150, 7.0, 33, 10, 5.65),
        ("Caramel Macchiato", "Espresso", "Grande", "Oat Milk", 270, 150, 8.0, 29, 3, 6.45),
        ("Caramel Macchiato", "Espresso", "Venti", "2% Milk", 310, 150, 9.0, 42, 13, 6.15),

        # Flat White
        ("Flat White", "Espresso", "Tall", "Whole Milk", 170, 130, 9.0, 13, 9, 4.95),
        ("Flat White", "Espresso", "Grande", "Whole Milk", 220, 195, 11.0, 17, 12, 5.65),
        ("Vanilla Oat Flat White", "Espresso", "Grande", "Oat Milk", 230, 195, 8.0, 18, 3, 6.45),

        # Cold Brew & Nitro
        ("Cold Brew", "Cold Brew", "Tall", "None", 5, 155, 0.0, 0, 0, 4.25),
        ("Cold Brew", "Cold Brew", "Grande", "None", 5, 205, 0.0, 0, 0, 4.75),
        ("Cold Brew", "Cold Brew", "Venti", "None", 5, 310, 0.0, 0, 1, 5.25),
        ("Vanilla Sweet Cream Cold Brew", "Cold Brew", "Grande", "Cream", 110, 185, 6.0, 14, 1, 5.45),
        ("Vanilla Sweet Cream Cold Brew", "Cold Brew", "Venti", "Cream", 200, 275, 11.0, 23, 2, 5.95),
        ("Nitro Cold Brew", "Cold Brew", "Grande", "None", 5, 280, 0.0, 0, 0, 5.45),

        # Iced Shaken Espresso
        ("Iced Shaken Espresso", "Iced Espresso", "Grande", "2% Milk", 100, 225, 2.0, 14, 2, 4.65),
        ("Brown Sugar Oat Iced Shaken Espresso", "Iced Espresso", "Grande", "Oat Milk", 120, 255, 3.5, 12, 2, 5.95),

        # Frappuccino (Blended)
        ("Caramel Frappuccino", "Frappuccino", "Tall", "Whole Milk", 260, 65, 11.0, 37, 3, 5.25),
        ("Caramel Frappuccino", "Frappuccino", "Grande", "Whole Milk", 380, 100, 16.0, 54, 5, 5.95),
        ("Mocha Frappuccino", "Frappuccino", "Grande", "Whole Milk", 370, 100, 15.0, 51, 5, 5.95),

        # Brewed Coffee
        ("Pike Place Roast", "Brewed Coffee", "Tall", "None", 5, 235, 0.0, 0, 1, 2.95),
        ("Pike Place Roast", "Brewed Coffee", "Grande", "None", 5, 310, 0.0, 0, 1, 3.45),
        ("Pike Place Roast", "Brewed Coffee", "Venti", "None", 5, 410, 0.0, 0, 2, 3.95),

        # Teas & Refreshers
        ("Chai Tea Latte", "Tea", "Grande", "2% Milk", 240, 95, 4.5, 42, 8, 5.25),
        ("Matcha Tea Latte", "Tea", "Grande", "2% Milk", 240, 80, 7.0, 32, 12, 5.45),
        ("Strawberry Acai Refresher", "Refresher", "Grande", "None", 100, 50, 0.0, 20, 1, 4.95),
        ("Mango Dragonfruit Refresher", "Refresher", "Grande", "None", 100, 45, 0.0, 19, 1, 4.95),
    ]

    cur.executemany("""
    INSERT INTO starbucks_drinks (
        beverage_name, category, size, milk_type, calories, caffeine_mg, total_fat_g, sugar_g, protein_g, price_usd
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_drinks)

    conn.commit()
    count = cur.execute("SELECT count(*) FROM starbucks_drinks").fetchone()[0]
    conn.close()
    print(f"Seeded {count} drinks into {DB_PATH}")

if __name__ == "__main__":
    create_and_seed_db()
