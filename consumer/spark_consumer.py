import os
import json
import psycopg2
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

# ---------- config ----------
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "transactions")
SUS_TOPIC = os.environ.get("SUS_TOPIC", "suspicious-transactions")
SPARK_APP_NAME = os.environ.get("SPARK_APP_NAME", "FraudShield-SparkConsumer")

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ.get("DB_NAME", "fraudshield")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASS = os.environ.get("DB_PASS", "admin123")

THRESHOLD = float(os.environ.get("FRAUD_THRESHOLD", 3000))

# ---------- Spark session ----------
spark = SparkSession.builder \
    .appName(SPARK_APP_NAME) \
    .master(os.environ.get("SPARK_MASTER", "local[*]")) \
    .config("spark.sql.shuffle.partitions", "2") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0") \
    .getOrCreate()

# ---------- schema ----------
schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("customer_id", IntegerType(), True),
    StructField("customer_name", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("currency", StringType(), True),
    StructField("merchant", StringType(), True),
    StructField("location", StringType(), True),
    StructField("status", StringType(), True),
    StructField("card_type", StringType(), True)
])

# ---------- read stream ----------
raw = (
    spark.readStream
         .format("kafka")
         .option("kafka.bootstrap.servers", KAFKA_BROKER)
         .option("subscribe", KAFKA_TOPIC)
         .option("startingOffsets", "latest")
         .load()
)

json_df = raw.selectExpr("CAST(value AS STRING) as json_value")
transactions = json_df.select(from_json(col("json_value"), schema).alias("data")).select("data.*")

# add fraud flag
flagged = transactions.withColumn("is_suspicious", when(col("amount") > THRESHOLD, True).otherwise(False))

# ---------- helper to write each micro-batch ----------
def process_batch(batch_df, batch_id):
    if batch_df.rdd.isEmpty():
        return

    rows = batch_df.collect()

    # print transactions
    for r in rows:
        txn = {
            "transaction_id": r.transaction_id,
            "timestamp": r.timestamp,
            "customer_id": r.customer_id,
            "customer_name": r.customer_name,
            "amount": r.amount,
            "currency": r.currency,
            "merchant": r.merchant,
            "location": r.location,
            "status": r.status,
            "card_type": r.card_type,
            "is_suspicious": r.is_suspicious
        }

        if r.is_suspicious:
            print(f"🚨 Suspicious transaction detected: {json.dumps(txn, indent=2)}")
        else:
            print(f"✅ Normal transaction: {json.dumps(txn, indent=2)}")

    # upsert to Postgres
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    cursor = conn.cursor()
    sql = """
    INSERT INTO transactions (
        transaction_id, timestamp, customer_id, customer_name,
        amount, currency, merchant, location, status, card_type, is_suspicious
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (transaction_id) DO UPDATE
      SET is_suspicious = EXCLUDED.is_suspicious;
    """
    data = [
        (
            r.transaction_id, r.timestamp, r.customer_id, r.customer_name,
            r.amount, r.currency, r.merchant, r.location, r.status, r.card_type, r.is_suspicious
        )
        for r in rows
    ]
    try:
        cursor.executemany(sql, data)
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# ---------- write suspicious transactions to Kafka ----------
sus_transactions = flagged.filter(col("is_suspicious") == True)
sus_kafka = sus_transactions.selectExpr(
    "CAST(transaction_id AS STRING) as key",
    "to_json(struct(*)) AS value"
)

sus_stream = sus_kafka.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("topic", SUS_TOPIC) \
    .option("checkpointLocation", "/tmp/spark_checkpoint_sus") \
    .start()

# ---------- start main streaming query ----------
query = flagged.writeStream \
    .foreachBatch(process_batch) \
    .start()

query.awaitTermination()
sus_stream.awaitTermination()
