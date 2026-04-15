#!/usr/bin/env python3
"""
One-time migration script: imports config/stocks.json into MariaDB.

Usage (from repo root):
    python db/migrate_from_json.py

Requires DB credentials in .env (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME).
The target table must already exist — run db/init.sql first.
"""
import json
import os
import sys

import pymysql
from dotenv import load_dotenv

load_dotenv()

STOCKS_JSON = os.path.join(os.path.dirname(__file__), '..', 'config', 'stocks.json')

INSERT_SQL = """
    INSERT INTO stocks
        (symbol, name, sector, currency, initial_value, initial_quantity,
         initial_date, upper_threshold, lower_threshold, purchase_fee,
         sold, sell_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def main():
    with open(STOCKS_JSON) as f:
        data = json.load(f)

    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4',
    )

    count = 0
    with conn:
        with conn.cursor() as cursor:
            for stock in data.get('stocks', []):
                cursor.execute(INSERT_SQL, (
                    stock['symbol'],
                    stock['name'].strip(),
                    stock['sector'],
                    stock['currency'],
                    stock['initial_value'],
                    stock.get('initial_quantity', 0),
                    stock['initial_date'],
                    stock.get('upper_threshold', -1),
                    stock.get('lower_threshold', -1),
                    stock.get('purchase_fee'),
                    0,
                    None,
                ))
                count += 1

            for stock in data.get('successful_exits', []):
                cursor.execute(INSERT_SQL, (
                    stock['symbol'],
                    stock['name'].strip(),
                    stock['sector'],
                    stock['currency'],
                    stock['initial_value'],
                    stock.get('initial_quantity', 0),
                    stock['initial_date'],
                    stock.get('upper_threshold', -1),
                    stock.get('lower_threshold', -1),
                    stock.get('purchase_fee'),
                    1,
                    stock.get('sell_date'),
                ))
                count += 1

        conn.commit()

    print(f"Migration complete: {count} rows inserted.")


if __name__ == '__main__':
    main()
