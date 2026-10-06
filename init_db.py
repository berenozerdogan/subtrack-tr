import sqlite3

conn = sqlite3.connect("subtrack.db")
c = conn.cursor()

# Tabloları oluştur
c.execute("""
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    brand_color TEXT NOT NULL,
    icon_class TEXT NOT NULL
);
""")

c.execute("""
CREATE TABLE IF NOT EXISTS service_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER REFERENCES services(id),
    plan_name TEXT NOT NULL,
    current_price REAL NOT NULL,
    billing_cycle TEXT DEFAULT 'monthly'
);
""")

c.execute("""
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER REFERENCES service_plans(id),
    price REAL NOT NULL,
    change_date TEXT NOT NULL
);
""")

# Türkiye Popüler Servis Kataloğu (Seed Data)
services_data = [
    # slug, name, category, brand_color, icon_class
    ("spotify", "Spotify", "Müzik", "#1DB954", "fa-brands fa-spotify"),
    ("netflix", "Netflix", "Dizi & Film", "#E50914", "fa-solid fa-film"),
    ("youtube", "YouTube Premium", "Video & Müzik", "#FF0000", "fa-brands fa-youtube"),
    ("disney", "Disney+", "Dizi & Film", "#113CCF", "fa-solid fa-clapperboard"),
    ("amazon-prime", "Amazon Prime", "Alışveriş & Dizi", "#00A8E1", "fa-brands fa-amazon"),
    ("chatgpt", "ChatGPT Plus", "Yapay Zekâ", "#10A37F", "fa-solid fa-robot"),
    ("icloud", "Apple iCloud+", "Depolama", "#007AFF", "fa-brands fa-apple"),
    ("google-one", "Google One", "Depolama", "#4285F4", "fa-brands fa-google"),
    ("xbox-gamepass", "Xbox Game Pass", "Oyun", "#107C10", "fa-brands fa-xbox"),
    ("playstation-plus", "PlayStation Plus", "Oyun", "#003791", "fa-brands fa-playstation"),
    ("blutv", "BluTV", "Dizi & Film", "#00D2C4", "fa-solid fa-tv"),
    ("exxen", "Exxen", "Dizi & Spor", "#FFD200", "fa-solid fa-futbol"),
    ("gain", "Gain", "Dizi & Belgesel", "#2563EB", "fa-solid fa-play"),
    ("duolingo", "Duolingo Super", "Eğitim", "#58CC02", "fa-solid fa-language"),
    ("apple-music", "Apple Music", "Müzik", "#FA2D48", "fa-solid fa-music")
]

for slug, name, cat, color, icon in services_data:
    c.execute("""
        INSERT OR IGNORE INTO services (slug, name, category, brand_color, icon_class)
        VALUES (?, ?, ?, ?, ?)
    """, (slug, name, cat, color, icon))

# Planlar ve Güncel TL Fiyatları (Örnek Türkiye Fiyatları)
plans_data = [
    # (service_slug, plan_name, current_price)
    ("spotify", "Öğrenci", 32.99),
    ("spotify", "Bireysel", 59.99),
    ("spotify", "Duo (2 Kişilik)", 79.99),
    ("spotify", "Aile (6 Kişilik)", 99.99),

    ("netflix", "Temel Plan (720p)", 149.99),
    ("netflix", "Standart Plan (1080p)", 229.99),
    ("netflix", "Özel Plan (4K)", 299.99),

    ("youtube", "Öğrenci", 52.99),
    ("youtube", "Bireysel", 79.99),
    ("youtube", "Aile", 159.99),

    ("disney", "Standart", 134.99),
    ("disney", "Premium (4K)", 164.99),

    ("amazon-prime", "Aylık Standart", 39.00),

    ("chatgpt", "Plus ($20/ay)", 700.00),

    ("icloud", "50 GB", 12.99),
    ("icloud", "200 GB", 39.99),
    ("icloud", "2 TB", 129.99),

    ("google-one", "100 GB", 19.99),
    ("google-one", "200 GB", 29.99),
    ("google-one", "2 TB", 99.99),

    ("xbox-gamepass", "PC Game Pass", 159.00),
    ("xbox-gamepass", "Ultimate", 209.00),

    ("playstation-plus", "Essential", 175.00),
    ("playstation-plus", "Extra", 260.00),
    ("playstation-plus", "Deluxe", 305.00),

    ("blutv", "Aylık", 99.90),
    ("exxen", "Reklamlı", 129.00),
    ("exxen", "Reklamsız", 179.00),
    ("gain", "Aylık Standart", 149.00),
    ("duolingo", "Super Bireysel", 79.99),
    ("apple-music", "Bireysel", 39.99)
]

for slug, plan_name, price in plans_data:
    c.execute("SELECT id FROM services WHERE slug = ?", (slug,))
    srv_row = c.fetchone()
    if srv_row:
        srv_id = srv_row[0]
        c.execute("""
            INSERT INTO service_plans (service_id, plan_name, current_price)
            VALUES (?, ?, ?)
        """, (srv_id, plan_name, price))

conn.commit()
conn.close()
print("✓ Veritabanı ve 15 servisin planları başarıyla kuruldu!")
