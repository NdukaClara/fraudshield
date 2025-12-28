# 📘 FraudShield Setup Instructions

This document provides a detailed, step-by-step guide for setting up and running the **FraudShield** project locally.  
It covers environment preparation, container setup, running the producer–consumer–loader flow, and launching the Streamlit dashboard.  

---

## 1️⃣ Prerequisites

Make sure the following are installed and working on your machine:

- **Docker Desktop** (latest stable version)  
- **Docker Compose v2** (included with Docker Desktop)  
- **Python 3.9+** (this project used 3.9.22)  
- **pip** available for that Python version  
-  **VS Code** 

---

## 2️⃣ Project Layout

Your repository structure should look like this:

```
fraudshield/
├── producer/
│ ├── producer.py # Streams transactions to Kafka
│ └── requirements.txt
│
├── consumer/
│ ├── simple_consumer.py # Basic consumer for manual debugging
│ ├── data_loader.py # Reads transactions and writes to Postgres
│ └── requirements.txt
│
├── dashboard/
│ └── app.py # Streamlit dashboard
│
├── db/
│ └── init.sql # Schema for transactions table
│
├── docker/
│ ├── Dockerfile
│ └── docker-compose.yml # Kafka, Zookeeper, Postgres, pgAdmin
│
├── .env # Environment variables (not committed)
├── docs/
│ └── setup_instructions.md # This setup guide
└── README.md
```


---

## 3️⃣ Create Local Project Environment

1. **Create project folder**  
   ```bash
   mkdir fraudshield
   cd fraudshield

2. **Create and activate virtual environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate   # macOS / Linux
    # Windows: .venv\Scripts\activate

3. **(Optional) Using pyenv:**
    ```bash
    pyenv local 3.9.22
    python -m venv .venv
    source .venv/bin/activate

 ---

## 4️⃣ Prepare `.env` and Docker Compose

### 1. Create a `.env` file in your project root.  
This file holds service credentials and configurations used by Docker Compose.

#### Example `.env`

```env
# PostgreSQL
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123
POSTGRES_DB=fraudshield

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@fraudshield.com
PGADMIN_DEFAULT_PASSWORD=admin123

# Kafka and Zookeeper
KAFKA_BROKER_ID=1
KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1
KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT

```
### 2. Ensure Docker Compose Configuration

Ensure that the file `fraudshield/docker/docker-compose.yml` exists and correctly references the environment variables from your `.env` file.  
The `.env` file you created will automatically be used when running Docker Compose.

---

#### 🐳 Docker Compose Configuration

Your Docker setup is defined in:  
`fraudshield/docker/docker-compose.yml`

It includes four main services:

| Service | Description |
|----------|-------------|
| **Zookeeper** | Manages Kafka coordination and cluster metadata. |
| **Kafka** | Message broker for real-time transaction streaming. |
| **PostgreSQL** | Stores all transaction data for analysis and dashboard visualization. |
| **pgAdmin** | Provides a web-based interface to manage and query the PostgreSQL database. |

---

## 5️⃣ Start Docker Services

From the docker/ directory:
``` bash
cd docker
docker compose --env-file ../.env up -d
```

Verify containers are running:
```bash
docker ps
```

You should see:

* zookeeper

* kafka

* postgres

* pgadmin

If a container fails to start, run:

``` bash
docker compose logs <service_name>
``` 

Once running:

Kafka is accessible at localhost:9092

Postgres is accessible at localhost:5432

pgAdmin is accessible at http://localhost:5050

Log in to pgAdmin using your credentials from the .env file.

**Notes:**
- Ensure Docker Desktop is running before executing any `docker` command.  
- If Docker works in your normal terminal but not inside VS Code, fix your shell PATH configuration:

For macOS / Linux:

```bash
export PATH="/usr/local/bin:$PATH"
```

Then restart VS Code for the change to take effect.

For Windows (PowerShell):

```powershell
setx PATH "$($env:PATH);C:\Program Files\Docker\Docker\resources\bin"
```

After running this, close and reopen both PowerShell and VS Code.

Once Docker is working correctly, start your services with:

```bash
docker compose up --build
```

This will launch Kafka, Zookeeper, PostgreSQL, and pgAdmin containers.

## 6️⃣ Initialize Database and Verify Schema

1. Ensure [db/init.sql](../db/init.sql) exists. It should define the `transactions` table.

2. When Postgres first starts, it automatically runs the `init.sql` file (mounted by Docker).

3. To verify, open a terminal in the Postgres container:

```bash
docker exec -it postgres bash
psql -U admin -d fraudshield
```

Inside psql, list tables:

```cs
\dt
```

4. Alternatively, via pgAdmin:

* Go to http://localhost:5050

* Login with admin@fraudshield.com / admin123

* Add server connection:

* Host: postgres

* Port: 5432

* Username: admin

* Password: admin123

* Database: fraudshield


## 7️⃣ Create Kafka Topics and Smoke Test

Before running the producer and consumer, you need to create the Kafka topic that will handle transaction messages.

Open a shell inside the Kafka container:

```bash
docker exec -it kafka bash
```

Create a new Kafka topic named transactions:

```bash
kafka-topics --create \
  --topic transactions \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
```

Verify that the topic was created successfully:

```bash
kafka-topics --list --bootstrap-server localhost:9092
```

Expected output:

```nginx
transactions
```
> **⚠️ Note: You do not need to manually create a second topic for suspicious transactions.
The consumer script automatically creates a new topic called suspicious-transactions the first time it detects and forwards a flagged transaction.

### 🧪 Smoke Test the Kafka Setup

You can quickly test that Kafka is working correctly by producing and consuming a test message.

**Produce a message:**

```bash
kafka-console-producer --topic transactions --bootstrap-server localhost:9092
```

Type a message, for example:

```json
{"transaction_id": "1", "amount": 250, "status": "success"}
```

Press Enter, then Ctrl + C to exit.

**Consume the message:**

In another terminal window, run:

```bash
docker exec -it kafka bash
kafka-console-consumer --topic transactions --from-beginning --bootstrap-server localhost:9092
```

You should see the message you just produced.

✅ At this point, your full infrastructure is ready:

* Kafka is streaming messages.

* PostgreSQL is initialized.

* pgAdmin is accessible.

The environment is prepared for running the Python producer, consumer, and data loader modules.


## 8️⃣ Run the Kafka Producer

The **producer** simulates real-time financial transactions and streams them into the Kafka topic (`transactions`).

Before running it, ensure that your virtual environment or Python environment has all required dependencies installed.

Navigate to the `producer` directory:

```bash
cd producer
```

Install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Then, start the producer:
```bash
python producer.py
```

This script will continuously generate synthetic transaction records using the Faker library and publish them to the Kafka topic.

Each record typically includes fields such as:

* `transaction_id`

* `customer_id`

* `merchant`

* `amount`

* `currency`

* `card_type`

* `status`

* `is_suspicious`

* `timestamp`

✅ Expected Output:
Your terminal should display logs confirming successful message publication to Kafka.

Example:

```css
[INFO] Sent transaction: {"transaction_id": "txn_102", "amount": 520.75, "status": "success"}
```

Keep this terminal running so the producer continues streaming new transactions.

---

## 9️⃣ Enable Fraud Detection Logic

FraudShield detects suspicious activity in real time by analyzing each incoming transaction before it’s written to the database.

This logic lives in consumer/consumer.py
.

### ⚙️ How It Works**

1. The consumer subscribes to the transactions topic.

2. It evaluates each transaction against a fraud threshold — for example, transactions where amount > 3000 are considered suspicious.

3. When a suspicious transaction is detected:
    * The transaction is tagged with "is_suspicious": true.

    * It’s forwarded to a new Kafka topic named suspicious-transactions.

        > You don’t need to manually create this topic — Kafka creates it automatically when the consumer first sends data to it.

4. All transactions (normal and suspicious) are also written to the PostgreSQL transactions table.

5. Suspicious transactions can later be queried or visualized separately for fraud analysis.

### 🔍 Example Threshold Rule

```python
if transaction["amount"] > 3000:
    transaction["is_suspicious"] = True
```

You can adjust this threshold later or extend it with additional features such as:

* Unusual transaction times

* Repeated failed attempts

* Suspicious merchant activity

* Machine learning anomaly detection

### 🧩 Conceptual Flow

```text
Producer  →  Kafka (transactions)  →  Consumer  →  PostgreSQL
                                      ↘
                                       ↘
                                 Kafka (suspicious-transactions)
```

This architecture makes the pipeline scalable and transparent. You can monitor both normal and suspicious streams independently.

## 🔟 Run the Kafka Consumer and Data Loader

The consumer subscribes to the same transactions Kafka topic, reads messages and performs fraud detection in real time, and hands them over to the data loader, which writes them into the PostgreSQL database.

Open a new terminal window and navigate to the consumer directory:

```bash
cd consumer
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Then, start the consumer:

```bash
python simple_consumer.py
```

* This script listens to the topic and processes each message as it arrives.
* If you get `NoBrokersAvailable`, verify Kafka is reachable at `localhost:9092`.
* The consumer terminal will display each transaction as it’s processed.

Start the data loader: 

```bash
python data_loader.py
```

* This script consumes Kafka messages and inserts transactions into PostgreSQL.
* Transactions exceeding `$3000` will be flagged as suspicious and sent to the automatically created `suspicious-transactions` topic.
* All transactions will be inserted into PostgreSQL with the `is_suspicious` column appropriately set.

To verify data insertion, connect to Postgres via the container:

```bash
docker exec -it postgres psql -U admin -d fraudshield
```

Run a quick query:

```sql
SELECT COUNT(*) FROM transactions;
SELECT * FROM transactions WHERE is_suspicious = true LIMIT 5;
```

You should see flagged transactions appear as the consumer runs.

## 1️⃣1️⃣ Verify Fraud Detection in pgAdmin

After running both the producer and consumer, you can visually confirm that transactions including flagged suspicious ones are being written correctly into PostgreSQL.

### 🧭 Access pgAdmin

1. Open your browser and go to http://localhost:5050

2. Log in with the credentials from your .env file:

    * Email: admin@fraudshield.com

    * Password: admin123

3. In the pgAdmin interface, right-click on Servers → Create → Server…, then enter:

    * Name: FraudShield

    * Host name: postgres

    * Port: 5432

    * Username: admin

    * Password: admin123

    * Database: fraudshield

Click **Save**.

### 📊 Verify the Transactions Table

Once connected:
1. Expand the database tree:
`fraudshield → Schemas → public → Tables → transactions`

2. Right-click **transactions → View/Edit Data → All Rows**

You should see a growing list of live transactions streaming in from Kafka.
Each record includes columns such as:

transaction_id	customer_id	  customer_name	  merchant	amount	currency	status	is_suspicious	timestamp


### 🚨 Confirm Suspicious Transactions

Scroll through the dataset and look for rows where:

`is_suspicious = true`

These indicate transactions that exceeded the fraud threshold (e.g., amount > 3000) and were automatically:

* Published to the `suspicious-transactions` Kafka topic, and

* Stored in the same `transactions` table for unified historical tracking.

You can also run a quick SQL filter directly inside pgAdmin’s **Query Tool**:

```sql
SELECT transaction_id, customer_id, merchant, amount, timestamp
FROM transactions
WHERE is_suspicious = true
ORDER BY timestamp DESC;
```

✅ Expected Output:
You should see a list of recently flagged transactions, reflecting the fraud detection logic from your Kafka consumer.

## 1️⃣2️⃣ Launch the Streamlit Dashboard

The Streamlit dashboard provides a real-time analytical view of all transactions flowing through the FraudShield pipeline, from generation to fraud detection and database storage.

It connects directly to PostgreSQL and visualizes key transaction trends, suspicious activity, and customer insights using Plotly-powered charts.

### 🧠 Overview

Once your producer and consumer are running:

* New transactions are continuously written to PostgreSQL.

* Each record includes an is_suspicious flag generated by the consumer.

* The dashboard reads this data and renders interactive charts that update on refresh.

You can explore:

* Real-time transaction summaries

* Suspicious vs normal activity breakdown

* Monthly and daily transaction trends

* Top suspicious customers and fraud hot-spots

* Average transaction amounts and card type distributions

### ⚙️ Setup

Navigate to the dashboard directory:

```bash
cd dashboard
```

Install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
``` 

🚀 Run the Dashboard

Start the Streamlit app:

```bash
streamlit run app.py
```

Then open your browser and visit:

```arduino
http://localhost:8501
```

You should see the FraudShield Real-Time Dashboard with live data from your PostgreSQL database.

### 📊 Key Dashboard Sections
1️⃣ General Transaction Insights

Interactive charts showing the distribution of normal vs suspicious transactions, transaction status breakdown, and average amount by status.

2️⃣ Transaction Trends

Monthly line charts visualizing total transaction volume and average transaction amount trends over time.

3️⃣ Location Insights

Top 10 most active locations, with histograms and box plots highlighting where suspicious transactions are concentrated.

4️⃣ Suspicious Customer Leaderboard

Leaderboard of customers with the highest count and total value of flagged transactions, along with their most recent activity.

5️⃣ Fraud Activity Heatmap

Bar-based heatmap tracking suspicious transaction frequency by month — helps identify spikes in fraudulent activity.

6️⃣ Latest Transactions

Table view of the most recent transactions, including the latest suspicious events for quick review.

### 🔄 Refreshing Data

Use the Refresh Data button in the sidebar to manually reload the most recent transactions from PostgreSQL.
A timestamp is displayed to confirm the last refresh time.

### ✅ Expected Output

You should see:

* Dynamic metrics for total, suspicious, and normal transactions.

* Interactive charts built with Plotly.

* Continuously updated records reflecting real-time ingestion.

If you see an empty dashboard, verify that your consumer is running and writing data into the `transactions` table.


## 1️⃣3️⃣ Cleanup and Maintenance

After testing or visualizing data in the Streamlit dashboard, you can safely stop all running services and background processes to free up system resources.

### 🧩 Stop the Producer and Consumer

If your producer and consumer scripts are still running in separate terminals, stop them manually with Ctrl + C in each terminal.

This halts the continuous production and consumption of transactions from the Kafka topic.

### 🐳 Stop Docker Services

Pause or close Docker Desktop, or simply bring down all containers from the project:

```bash
docker compose down
```

This will stop and remove the containers for:

* Zookeeper

* Kafka

* PostgreSQL

* pgAdmin

Once stopped, your local environment will be clean and idle until you decide to start it again.

## 1️⃣4️⃣ Next Steps

The next phase of this project will focus on extending real-time fraud detection using Spark Structured Streaming and machine learning (ML) models.

These components will enable continuous data ingestion, feature engineering, and predictive classification of suspicious transactions, making FraudShield smarter and more scalable.

Once integrated, this section (and the README) will be updated with the new setup and instructions.