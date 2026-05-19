CREATE_MONITORS_TABLE = """
CREATE TABLE IF NOT EXISTS monitors (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    country          TEXT    NOT NULL,
    retailer         TEXT    NOT NULL,
    product_title    TEXT    NOT NULL,
    brand            TEXT,
    model            TEXT,
    screen_size_inch REAL,
    resolution       TEXT,
    refresh_rate     INTEGER,
    panel_type       TEXT,
    condition        TEXT    DEFAULT 'unknown',
    price            REAL,
    currency         TEXT,
    availability     TEXT,
    product_url      TEXT    UNIQUE NOT NULL,
    image_url        TEXT,
    crawl_date       TEXT    NOT NULL,
    created_at       TEXT    DEFAULT (datetime('now')),
    updated_at       TEXT    DEFAULT (datetime('now'))
);
"""

CREATE_CRAWL_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS crawl_logs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    site           TEXT    NOT NULL,
    country        TEXT    NOT NULL,
    status         TEXT    NOT NULL,
    products_found INTEGER DEFAULT 0,
    error_message  TEXT,
    started_at     TEXT,
    completed_at   TEXT,
    created_at     TEXT    DEFAULT (datetime('now'))
);
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_country    ON monitors(country);",
    "CREATE INDEX IF NOT EXISTS idx_brand      ON monitors(brand);",
    "CREATE INDEX IF NOT EXISTS idx_retailer   ON monitors(retailer);",
    "CREATE INDEX IF NOT EXISTS idx_crawl_date ON monitors(crawl_date);",
    "CREATE INDEX IF NOT EXISTS idx_price      ON monitors(price);",
]

UPSERT_MONITOR = """
INSERT INTO monitors (
    country, retailer, product_title, brand, model,
    screen_size_inch, resolution, refresh_rate, panel_type,
    condition, price, currency, availability,
    product_url, image_url, crawl_date
) VALUES (
    :country, :retailer, :product_title, :brand, :model,
    :screen_size_inch, :resolution, :refresh_rate, :panel_type,
    :condition, :price, :currency, :availability,
    :product_url, :image_url, :crawl_date
)
ON CONFLICT(product_url) DO UPDATE SET
    price        = excluded.price,
    availability = excluded.availability,
    image_url    = excluded.image_url,
    crawl_date   = excluded.crawl_date,
    updated_at   = datetime('now');
"""
