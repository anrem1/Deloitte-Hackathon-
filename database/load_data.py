"""
FlavorCraft Database Setup & Data Loader:

Loads ~9.1M rows across 25 tables into Xata PostgreSQL database.

This script handles schema creation and data loading for the FlavorCraft
menu engineering platform, implementing critical fixes for data type issues
and connection management.

Author: Knzy
Date: February 2026
"""

import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_batch
from pathlib import Path
import logging
import time
import os
from dotenv import load_dotenv
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

def get_connection():
    """Create new database connection."""
    return psycopg2.connect(**DB_CONFIG)

def clean_dataframe(df):
    """
    Clean DataFrame for PostgreSQL insertion.
    
    Critical fixes:
    1. Convert pandas float64 to Int64 for BIGINT columns (prevents overflow)
    2. Explicit boolean conversion (0/1 → True/False)
    3. Replace empty strings and NaN with None
    
    Args:
        df: pandas DataFrame
        
    Returns:
        Cleaned DataFrame ready for database insertion
    """
    df_clean = df.copy()
    
    # Replace empty/NaN values with None
    df_clean = df_clean.replace({'': None, 'nan': None, np.nan: None, 'NaN': None})
    df_clean = df_clean.where(pd.notna(df_clean), None)
    
    # Convert boolean fields explicitly
    boolean_fields = ['demo_mode', 'trainee_mode', 'requires_signature', 
                      'synchronized_to_accounting', 'mobile_phone_valid', 'email_valid']
    for col in boolean_fields:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].apply(lambda x: 
                True if x in (1, 1.0, '1', '1.0', 'True', 'true', 't') 
                else (False if x in (0, 0.0, '0', '0.0', 'False', 'false', 'f')  
                else None)
            )
    
    # Convert float64 to Int64 for integer columns
    # This prevents "bigint out of range" errors when pandas reads large integers as float64
    for col in df_clean.columns:
        if col not in boolean_fields and df_clean[col].dtype == 'float64':
            try:
                non_null = df_clean[col].dropna()
                if len(non_null) > 0 and all(non_null == non_null.astype(int)):
                    df_clean[col] = df_clean[col].astype('Int64')
            except:
                pass
    
    return df_clean

def load_table(csv_path, table_name, log_interval=100000):
    """
    Load data from CSV into database table.
    
    Strategy:
    - Read CSV in 10K row chunks
    - Reconnect to database every chunk (prevents Xata timeout after 45 min)
    - Use ON CONFLICT DO NOTHING for idempotent loading
    - Commit after each chunk for progress persistence
    
    Args:
        csv_path: Path to CSV file
        table_name: PostgreSQL table name
        log_interval: Log progress every N rows
        
    Returns:
        Total rows processed
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"Loading: {table_name}")
    logger.info(f"Source: {csv_path.name}")
    logger.info(f"Size: {csv_path.stat().st_size / 1024 / 1024:.0f} MB")
    logger.info('='*70)
    
    start_time = time.time()
    total_rows = 0
    chunk_count = 0
    
    conn = None
    cursor = None
    
    try:
        for chunk in pd.read_csv(csv_path, chunksize=10000, low_memory=False):
            chunk_count += 1
            
            # Reconnect every chunk to prevent Xata timeout (45 min limit)
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            except:
                pass
            
            conn = get_connection()
            cursor = conn.cursor()
            
            chunk_clean = clean_dataframe(chunk)
            if chunk_clean.empty:
                continue
            
            columns = list(chunk_clean.columns)
            
            # Build INSERT query with conflict handling
            insert_query = sql.SQL(
                "INSERT INTO {table} ({fields}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING"
            ).format(
                table=sql.Identifier(table_name),
                fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
                placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
            )
            
            data = [tuple(row) for row in chunk_clean.values]
            
            try:
                execute_batch(cursor, insert_query, data, page_size=1000)
                conn.commit()
                total_rows += len(chunk_clean)
                
                if total_rows % log_interval == 0:
                    elapsed = time.time() - start_time
                    rate = total_rows / elapsed if elapsed > 0 else 0
                    logger.info(f"{total_rows:,} rows | {rate:.0f} rows/sec")
            except Exception as e:
                logger.warning(f"Chunk {chunk_count} error: {str(e)[:100]}")
                conn.rollback()
                continue
        
        elapsed = time.time() - start_time
        logger.info(f"✅ {table_name} DONE: {total_rows:,} rows in {elapsed/60:.1f} min")
        return total_rows
        
    except Exception as e:
        logger.error(f"{table_name} FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 0
    finally:
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except:
            pass

def create_schema():
    """Execute schema creation SQL."""
    schema_path = Path(__file__).parent / 'schema_xata.sql'
    
    if not schema_path.exists():
        logger.error(f"Schema file not found: {schema_path}")
        return False
    
    logger.info("Creating database schema...")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Schema created successfully")
        return True
    except Exception as e:
        logger.error(f"Schema creation failed: {e}")
        return False

def get_table_status():
    """Get row counts for all tables."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        status = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            status[table] = count
        
        cursor.close()
        conn.close()
        
        return status
    except Exception as e:
        logger.error(f"Failed to get table status: {e}")
        return {}

def main():
    """Main execution function."""
    logger.info("\n" + "="*70)
    logger.info("FlavorCraft Database Setup")
    logger.info("="*70)
    
    # Check before loading
    logger.info("\nCurrent database status:")
    status = get_table_status()
    if status:
        total_rows = sum(status.values())
        logger.info(f"  Total rows: {total_rows:,}")
        logger.info(f"  Tables: {len(status)}")
    else:
        logger.info("  Database empty or not accessible")
        logger.info("\nCreating schema...")
        if not create_schema():
            logger.error("Schema creation failed. Exiting.")
            return
    
    # Define data directories
    DATA_DIR_PART1 = Path(__file__).parent.parent / 'data' / 'Menu Engineering Part 1'
    DATA_DIR_PART2 = Path(__file__).parent.parent / 'data' / 'Menu Engineering Part 2'
    DATA_DIR_INV = Path(__file__).parent.parent / 'data' / 'Inventory Management'
    
    # Load dimension tables first (smaller, needed for foreign keys)
    logger.info("\n" + "="*70)
    logger.info("PHASE 1: Loading Dimension Tables")
    logger.info("="*70)
    
    dimension_files = [
        (DATA_DIR_PART2 / 'dim_users.csv', 'dim_users'),
        (DATA_DIR_PART2 / 'dim_menu_items.csv', 'dim_menu_items'),
        (DATA_DIR_PART2 / 'dim_items.csv', 'dim_items'),
        (DATA_DIR_PART2 / 'dim_sections.csv', 'dim_sections'),
        (DATA_DIR_PART2 / 'dim_add_ons.csv', 'dim_add_ons'),
        (DATA_DIR_PART2 / 'dim_products.csv', 'dim_products'),
        (DATA_DIR_PART2 / 'dim_campaigns.csv', 'dim_campaigns'),
        (DATA_DIR_PART2 / 'dim_taxonomy_terms.csv', 'dim_taxonomy_terms'),
    ]
    
    for csv_path, table_name in dimension_files:
        if csv_path.exists():
            load_table(csv_path, table_name, log_interval=50000)
    
    # Load fact tables (large transaction data)
    logger.info("\n" + "="*70)
    logger.info("PHASE 2: Loading Fact Tables")
    logger.info("="*70)
    
    # Payments (4.9M rows - largest table)
    logger.info("\nPAYMENTS")
    load_table(DATA_DIR_PART1 / 'fct_payments_part1.csv', 'fct_payments')
    load_table(DATA_DIR_PART2 / 'fct_payments_part2.csv', 'fct_payments')
    
    # App Events (2.7M rows - second largest)
    logger.info("\nAPP EVENTS")
    load_table(DATA_DIR_PART2 / 'fct_app_events.csv', 'fct_app_events')
    
    # Order Items (2M rows)
    logger.info("\nORDER ITEMS")
    load_table(DATA_DIR_INV / 'fct_order_items.csv', 'fct_order_items')
    
    # Final status
    logger.info("\n" + "="*70)
    logger.info("FINAL DATABASE STATUS")
    logger.info("="*70)
    
    final_status = get_table_status()
    if final_status:
        total_rows = sum(final_status.values())
        logger.info(f"\nTotal rows loaded: {total_rows:,}")
        logger.info(f"Tables populated: {len(final_status)}\n")
        
        # Show top tables by size
        sorted_tables = sorted(final_status.items(), key=lambda x: x[1], reverse=True)
        logger.info("Largest tables:")
        for table, count in sorted_tables[:10]:
            logger.info(f"  {table}: {count:,} rows")
    
    logger.info("\n" + "="*70)
    logger.info("DATABASE SETUP COMPLETE")
    logger.info("="*70)

if __name__ == '__main__':
    main()
