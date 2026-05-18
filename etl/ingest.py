import pandas as pd
import os
from config import get_connection

RAW_DATA_PATH = r"E:\SalesForecasting\data\raw\store-sales-time-series-forecasting"

def load_sales():
    print("Loading sales data...")
    conn = get_connection()
    cursor = conn.cursor()
    
    filepath = os.path.join(RAW_DATA_PATH, "train.csv")
    chunk_size = 50000
    total_rows = 0
    
    for chunk in pd.read_csv(filepath, chunksize=chunk_size):
        # Filter to 2015-2017 only
        chunk['date'] = pd.to_datetime(chunk['date'])
        chunk = chunk[
            (chunk['date'] >= '2015-01-01') & 
            (chunk['date'] <= '2017-08-15')
        ]
        chunk['onpromotion'] = chunk['onpromotion'].astype(bool)
        
        for _, row in chunk.iterrows():
            cursor.execute("""
                INSERT INTO raw.sales (id, date, store_nbr, family, sales, onpromotion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (row['id'], row['date'], row['store_nbr'], 
                  row['family'], row['sales'], row['onpromotion']))
        
        conn.commit()
        total_rows += len(chunk)
        print(f"  Loaded {total_rows} rows so far...")
    
    cursor.close()
    conn.close()
    print(f"Sales load complete. Total rows: {total_rows}")

def load_stores():
    print("Loading stores data...")
    conn = get_connection()
    cursor = conn.cursor()
    
    filepath = os.path.join(RAW_DATA_PATH, "stores.csv")
    df = pd.read_csv(filepath)
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO raw.stores (store_nbr, city, state, type, cluster)
            VALUES (%s, %s, %s, %s, %s)
        """, (row['store_nbr'], row['city'], row['state'], 
              row['type'], row['cluster']))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Stores load complete. Total rows: {len(df)}")

def load_oil():
    print("Loading oil data...")
    conn = get_connection()
    cursor = conn.cursor()
    
    filepath = os.path.join(RAW_DATA_PATH, "oil.csv")
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    df['dcoilwtico'] = pd.to_numeric(df['dcoilwtico'], errors='coerce')
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO raw.oil (date, dcoilwtico)
            VALUES (%s, %s)
        """, (row['date'], None if pd.isna(row['dcoilwtico']) 
              else row['dcoilwtico']))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Oil load complete. Total rows: {len(df)}")

def load_holidays():
    print("Loading holidays data...")
    conn = get_connection()
    cursor = conn.cursor()
    
    filepath = os.path.join(RAW_DATA_PATH, "holidays_events.csv")
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    df['transferred'] = df['transferred'].astype(bool)
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO raw.holidays 
            (date, type, locale, locale_name, description, transferred)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (row['date'], row['type'], row['locale'], 
              row['locale_name'], row['description'], row['transferred']))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Holidays load complete. Total rows: {len(df)}")

if __name__ == "__main__":
    load_stores()
    load_oil()
    load_holidays()
    load_sales()
    print("\nAll data loaded successfully!")