from kafka import KafkaConsumer
import psycopg2
import json
import time

# PostgreSQL connection
conn = psycopg2.connect(
    host="localhost",
    database="fraudshield",
    user="admin",
    password="admin123",
    port="5432"
)
cursor = conn.cursor()

# Kafka consumer setup
consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

print("🚀 Listening to Kafka topics: transactions & suspicious-transactions")

def insert_transaction(txn):
    cursor.execute(f"""
        INSERT INTO transactions (
            transaction_id, timestamp, customer_id, customer_name, amount, currency, merchant, location, status, card_type, is_suspicious
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
         ON CONFLICT (transaction_id) DO NOTHING;
    """, (
        txn.get("transaction_id"),
        txn.get("timestamp"),
        txn.get("customer_id"),
        txn.get("customer_name"),
        txn.get("amount"),
        txn.get("currency"),
        txn.get("merchant"),
        txn.get("location"),
        txn.get("status"),
        txn.get("card_type"),
        txn.get("is_suspicious", False)
    ))
    conn.commit()

try:
    THRESHOLD = 3000  # Flag any transaction above this as suspicious
    count = 0

    for message in consumer:
        txn = message.value
        txn["is_suspicious"] = txn["amount"] > THRESHOLD

        insert_transaction(txn)
        count += 1

        if txn["is_suspicious"]:
            print(f"🚨 Suspicious transaction: {txn['transaction_id']} (${txn['amount']})")
        else:
            print(f"✅ Normal transaction: {txn['transaction_id']} (${txn['amount']})")

        # Commit to DB every 50 transactions
        if count % 50 == 0:
            conn.commit()
            print(f"💾 Committed {count} transactions to database...")

except KeyboardInterrupt:
    print("\n🛑 Stopping consumer...")

finally:
    # Final commit and cleanup
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database connection closed.")
