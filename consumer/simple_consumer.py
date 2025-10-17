from kafka import KafkaConsumer, KafkaProducer
import json

# Connect to Kafka
consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    group_id='fraudshield-loader',        # unique consumer group
    enable_auto_commit=False,             # we will commit manually
    auto_offset_reset='latest'          # start from earliest messages only if new group
)

# Optional: producer for sending suspicious transactions to another topic
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("👀 Listening for transactions...")

# Fraud detection rule: flag transactions over $1000
THRESHOLD = 3000

for message in consumer:
    transaction = message.value
    amount = transaction.get('amount', 0)

    if amount > THRESHOLD:
        transaction['is_suspicious'] = True
        print(f"🚨 Suspicious transaction detected: {transaction}")
        producer.send('suspicious-transactions', value=transaction)
    else:
        transaction['is_suspicious'] = False
        print(f"✅ Normal transaction: {transaction}")
