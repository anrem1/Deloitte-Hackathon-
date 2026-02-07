# FlavorCraft Database Setup

Complete database infrastructure for the FlavorCraft menu engineering platform, managing ~9.1 million rows across 25 tables in Xata PostgreSQL.

## Database Overview

**Platform:** Xata PostgreSQL 18.1 (Cloud-hosted, 15GB free tier)  
**Total Size:** ~2.5GB of CSV data  
**Tables:** 25 (13 dimension tables + 12 fact tables)  
**Total Rows:** 9,100,000+

### Key Tables

| Table | Rows | Description |
|-------|------|-------------|
| `fct_payments` | 4,899,883 | Payment transactions (Stripe, cash, etc.) |
| `fct_app_events` | 2,723,944 | User app interactions and events |
| `fct_order_items` | 1,999,341 | Individual items in orders |
| `dim_items` | 87,713 | Complete menu item catalog |
| `dim_menu_items` | 30,407 | Active menu items with pricing |
| `dim_users` | 22,955 | Customer profiles with CLTV |

## Architecture

```
database/
├── schema_xata.sql          # PostgreSQL schema (25 tables)
├── load_data.py            # Master data loader script
├── check_status.py         # Database status checker
├── .env                    # Database credentials (NOT in git)
├── .env.example            # Template for credentials
└── README.md              # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL client (optional, for manual queries)
- 3GB+ available disk space for data processing

### Installation

1. **Install dependencies:**
```bash
pip install -r ../requirements.txt
```

Required packages:
- `pandas` - CSV data processing
- `psycopg2-binary` - PostgreSQL adapter
- `python-dotenv` - Environment variable management
- `numpy` - Numerical operations

2. **Configure database credentials:**

Create `.env` file in the `database/` directory:

```bash
# Xata PostgreSQL Connection
DB_HOST=your-instance.xata.tech
DB_PORT=5432
DB_NAME=xata
DB_USER=xata
DB_PASSWORD=your-password-here
```

> ⚠️ **Security Note:** Never commit `.env` file to git. Use `.env.example` as template.

3. **Verify connection:**
```bash
python test_connection.py
```

### Data Loading

**Full Load (recommended for first time)**

```bash
python load_data.py
```

This will:
1. Create schema (25 tables with proper constraints)
2. Load dimension tables (~185K rows)
3. Load fact tables (~9M rows)
4. Report final status

**Estimated time:** 3-4 hours depending on network speed

### Verify Data

```bash
python check_status.py
```

Output:
```
Table Counts:
  dim_users: 22,955
  dim_menu_items: 30,407
  fct_payments: 4,899,883
  fct_app_events: 2,723,944
  fct_order_items: 1,999,341
  ...
Total: 9,100,000+ rows
```

## 🛠️ Technical Details

### Critical Fixes Implemented

During development, we encountered and resolved several data loading challenges:

#### 1. **Pandas Float64 → PostgreSQL BIGINT Issue**

**Problem:** Pandas reads large integers as `float64`, PostgreSQL rejects float values in BIGINT columns.

**Solution:**
```python
# Convert float64 to Int64 for integer columns
if df[col].dtype == 'float64':
    non_null = df[col].dropna()
    if len(non_null) > 0 and all(non_null == non_null.astype(int)):
        df[col] = df[col].astype('Int64')
```

#### 2. **Boolean Type Mismatch**

**Problem:** CSV contains 0/1 integers, PostgreSQL expects boolean type.

**Solution:**
```python
# Explicit boolean conversion
boolean_fields = ['demo_mode', 'trainee_mode', 'requires_signature']
for col in boolean_fields:
    df[col] = df[col].apply(lambda x: 
        True if x in (1, 1.0, '1') else False
    )
```

#### 3. **Xata Connection Timeout**

**Problem:** Xata closes connections after 45 minutes continuous operation (~1.4M rows).

**Solution:** Reconnect database every 10K rows (every chunk):
```python
for chunk in pd.read_csv(csv_path, chunksize=10000):
    conn.close()  # Close old connection
    conn = get_connection()  # Open new connection
    # Load chunk...
```

#### 4. **Schema Mismatches**

**Problem:** CSV columns contained mixed data types (e.g., `receipt_number` with both integers and strings).

**Solution:** Changed VARCHAR columns to TEXT for variable-length strings:
```sql
-- Before: receipt_number VARCHAR(50)
-- After:  receipt_number TEXT
```

### Loading Strategy

**Chunk Processing:**
- Read CSV in 10,000 row chunks
- Process and clean each chunk
- Insert with `ON CONFLICT (id) DO NOTHING` for idempotency
- Commit after each chunk for progress persistence

**Benefits:**
- Memory efficient (handles 1GB+ files)
- Resumable (reconnect picks up where left off)
- Safe (duplicates automatically skipped)
- Progress tracking (logs every 100K rows)

### Performance Metrics

| Operation | Rate | Time (estimate) |
|-----------|------|-----------------|
| Dimension tables | ~500 rows/sec | 5-10 minutes |
| Large fact tables | ~340 rows/sec | 2-3 hours |
| Full database | ~280 rows/sec | 3-4 hours |

*Note: Rates vary based on network connection and Xata server load.*

## 📋 Schema Documentation

### Dimension Tables (Reference Data)

- `dim_users` - Customer profiles with lifetime value, preferences
- `dim_menu_items` - Menu items with prices, categories, popularity
- `dim_items` - Full item catalog with descriptions
- `dim_add_ons` - Available add-ons and modifications
- `dim_sections` - Menu categories and sections
- `dim_products` - Base products and ingredients
- `dim_campaigns` - Marketing campaigns
- `dim_taxonomy_terms` - Classification terms

### Fact Tables (Transactional Data)

- `fct_payments` - All payment transactions (Stripe, cash, mobile pay)
- `fct_app_events` - User app interactions (views, clicks, sessions)
- `fct_order_items` - Line items in orders
- `fct_orders` - Order headers
- `fct_invoice_items` - Invoice line items
- `fct_campaigns` - Campaign performance

### Key Relationships

```
dim_users (1) ─── (N) fct_payments
         (1) ─── (N) fct_orders
         (1) ─── (N) fct_app_events

dim_menu_items (1) ─── (N) fct_order_items

fct_orders (1) ─── (N) fct_order_items
           (1) ─── (1) fct_payments
```

## 🔍 Common Queries

### Customer Lifetime Value Analysis
```sql
SELECT 
    user_id,
    cltv,
    orders,
    avg_order_value
FROM dim_users
WHERE cltv > 0
ORDER BY cltv DESC
LIMIT 100;
```

### Top Selling Items
```sql
SELECT 
    mi.name,
    mi.purchases,
    mi.price_in_user_currency
FROM dim_menu_items mi
ORDER BY mi.purchases DESC
LIMIT 20;
```

### Payment Methods Distribution
```sql
SELECT 
    provider,
    COUNT(*) as transactions,
    SUM(amount) as total_amount
FROM fct_payments
GROUP BY provider
ORDER BY transactions DESC;
```

## 🐛 Troubleshooting

### Connection Issues

**Error:** `could not connect to server`

**Solution:**
1. Verify `.env` credentials are correct
2. Check Xata instance is active
3. Confirm network connectivity

### Loading Issues

**Error:** `bigint out of range`

**Solution:** Already fixed in `load_data.py` with dtype conversion.

**Error:** `column "demo_mode" is of type boolean but expression is of type integer`

**Solution:** Already fixed with explicit boolean conversion.

## 📈 Database Statistics

After full load:

```
Total Tables: 25
Total Rows: 9,100,000+
Database Size: ~3.2 GB

Row Distribution:
  - Dimension tables: 185,194 (2%)
  - Fact tables: 8,915,000+ (98%)

Largest Tables:
  1. fct_payments: 4.9M rows (54%)
  2. fct_app_events: 2.7M rows (30%)
  3. fct_order_items: 2.0M rows (22%)
```

## 🤝 Team Contributions

**Database Team:**
- Schema design and optimization
- Data loading pipeline development
- Type mismatch resolution
- Connection management fixes
- Performance optimization
- Documentation

**Key Achievements:**
- ✅ Successfully loaded 9.1M+ rows
- ✅ Resolved pandas float64/PostgreSQL BIGINT incompatibility
- ✅ Implemented connection timeout mitigation
- ✅ Created idempotent, resumable loading process
- ✅ Optimized for 340+ rows/sec throughput

## 🔐 Security Notes

- **Never commit `.env` file** - contains sensitive credentials
- Use `.env.example` as template for team members
- Xata free tier doesn't require credit card
- No PII (Personally Identifiable Information) in exports

---

**Last Updated:** February 7, 2026  
**Database Version:** 1.0  
**Schema Version:** Final (Xata Production)
