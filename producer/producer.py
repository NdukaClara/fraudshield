from kafka import KafkaProducer
from faker import Faker
import json
import random
import time
from datetime import datetime, timedelta

# Initialize Faker for generating fake transaction data
fake = Faker()

# Define start and end dates for 2025
start_date = datetime(2025, 1, 1)
end_date = datetime.now()  # today, October 2025

# Create Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],     # Kafka broker address
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Convert Python dict to JSON bytes
)

topic_name = "transactions"  # Kafka topic name

# Function to simulate random transactions
def generate_transaction():
    transaction = {
        "transaction_id": fake.uuid4(),
        "timestamp": fake.date_time_between(start_date=start_date, end_date=end_date).isoformat(),
        "customer_id": fake.random_int(min=1000, max=9999),
        "customer_name": fake.name(),
        "amount": round(random.uniform(5.0, 5000.0), 2),
        "currency": "USD",
        "merchant": fake.company(),
        "location": fake.city(),
        "status": random.choice(["SUCCESS", "FAILED", "PENDING"]),
        "card_type": random.choice(["VISA", "MASTERCARD", "AMEX"]),
    }
    return transaction

# Send transactions to Kafka
if __name__ == "__main__":
    print("🚀 Starting transaction producer... Sending data to Kafka topic:", topic_name)
    while True:
        transaction = generate_transaction()
        producer.send(topic_name, transaction)
        print(f"✅ Sent: {transaction}")
        time.sleep(30)  # wait 30 second before sending the next transaction
