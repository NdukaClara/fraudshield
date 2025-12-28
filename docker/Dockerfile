# # Use official Spark image
# FROM apache/spark:3.5.0

# USER root
# WORKDIR /app

# # Install Python3 and pip
# RUN apt-get update && \
#     apt-get install -y python3 python3-pip wget && \
#     ln -s /usr/bin/python3 /usr/bin/python && \
#     rm -rf /var/lib/apt/lists/*

# # Install Python dependencies
# RUN pip install --no-cache-dir pyspark==3.5.0 kafka-python psycopg2-binary

# # Pre-download correct Kafka connector JAR for Scala 2.13
# RUN mkdir -p /opt/spark/jars && \
#     wget -O /opt/spark/jars/spark-sql-kafka-0-10_2.13-3.5.0.jar \
#     https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.13/3.5.0/spark-sql-kafka-0-10_2.13-3.5.0.jar && \
#     wget -O /opt/spark/jars/spark-token-provider-kafka-0-10_2.13-3.5.0.jar \
#     https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.13/3.5.0/spark-token-provider-kafka-0-10_2.13-3.5.0.jar

# # Copy consumer code
# WORKDIR /app/consumer
# COPY ../consumer .

# # Run consumer
# CMD ["python3", "spark_consumer.py"]
