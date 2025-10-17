# 🛡️ FraudShield — Real-Time Fraud Detection Pipeline

**FraudShield** is a real-time data engineering project designed to simulate how financial institutions handle and detect suspicious transactions in live data streams.

Built with **Kafka**, **PostgreSQL**, and **Streamlit**, the project demonstrates how streaming data pipelines can power real-time fraud analytics — from ingestion to visualization.

---

## 🧠 Project Overview

FraudShield explores how organizations that consume real-time data, especially banks and payment processors, manage transaction flows and identify anomalous patterns as data moves through the pipeline.

The system simulates:

- A **data producer** continuously generating synthetic financial transactions.  
- A **Kafka broker** that streams those transactions in real time.  
- A **consumer and loader service** that ingests and stores data in PostgreSQL.  
- A **Streamlit dashboard** for live analytics, fraud detection trends, and transaction summaries.

This pipeline mirrors how real-world systems detect fraud signals — whether through thresholds, metadata patterns, or customer behavior — as data flows from ingestion to analytics.

---

## 🧩 Architecture Overview

### Core Components

| **Layer**              | **Component**          | **Description**                                                                 |
|------------------------|------------------------|---------------------------------------------------------------------------------|
| Data Generation        | **Producer**           | Uses Faker to simulate financial transactions (customer, merchant, card type, status, etc.) |
| Message Queue          | **Apache Kafka**       | Streams real-time transactions between producer and consumer                   |
| Data Storage           | **PostgreSQL**         | Stores raw and processed transactions for querying and dashboard analysis       |
| Monitoring UI          | **Streamlit Dashboard**| Displays aggregated metrics, suspicious activity, and transaction insights      |
| Management Tools       | **pgAdmin**            | Provides visual database management and query interface                         |

---


## 📊 End-to-End Flow
```
                ┌────────────────────┐
                │   Data Producer    │
                │ (Kafka Producer)   │
                └────────┬───────────┘
                         │
                         ▼
                ┌────────────────────┐
                │      Kafka         │
                │ (Event Stream)     │
                └────────┬───────────┘
                         │
                         ▼
                ┌────────────────────┐
                │  Simple Consumer   │
                │ (Message Reader)   │
                └────────┬───────────┘
                         │
                         ▼
                ┌────────────────────┐
                │   Data Loader      │
                │ (Writes to DB)     │
                └────────┬───────────┘
                         │
                         ▼
                ┌────────────────────┐
                │     Postgres       │
                │ (Data Storage)     │
                └────────┬───────────┘
                         │
                         ▼
                ┌────────────────────┐
                │     Dashboard      │
                │ (Stream Analytics) │
                └────────────────────┘

```

## 🔄 Data Flow

### 1️⃣ Transaction Simulation  
A **Python-based producer** continuously generates transaction records with fields like amount, merchant, card type, and timestamps.  
Each record is published to a Kafka topic (`transactions`).

---

### 2️⃣ Real-Time Ingestion  
The **Kafka consumer** listens to the same topic and streams incoming messages.  
As transactions arrive, they’re processed and pushed into **PostgreSQL** through the **data loader service**.

---

### 3️⃣ Persistent Storage  
Each transaction is stored in the `transactions` table with columns like:

- `transaction_id`  
- `customer_id`  
- `merchant`  
- `amount`  
- `currency`  
- `card_type`  
- `status`  
- `is_suspicious`  
- `timestamp`

---

### 4️⃣ Analytics Dashboard  
The **Streamlit dashboard** connects directly to the Postgres database and provides:

- Transaction summaries and trends  
- Suspicious customer leaderboards  
- Real-time fraud insights  
- Monthly and daily transaction aggregations  

---

## ⚙️ Key Features

✅ **Real-Time Streaming:** Transaction data flows from producer → Kafka → Postgres continuously.  
✅ **Dynamic Fraud Tagging:** Randomized flags for `is_suspicious` simulate real fraud scenarios.  
✅ **Fully Containerized Environment:** All components (Kafka, Postgres, pgAdmin) run inside Docker.  
✅ **Data Persistence:** PostgreSQL stores each transaction for historical and analytical insights.  
✅ **Interactive Dashboard:** Built with Streamlit and Plotly for rich, real-time visualizations.  
✅ **Modular Design:** Independent Python modules for producing, consuming, loading, and analyzing data.  
✅ **Scalable Architecture:** Ready for future integration with Spark Structured Streaming and ML models.

---

## 🧱 Project Structure

```
fraudshield/
│
├── producer/
│   ├── producer.py               # Generates and streams transaction data
│   └── requirements.txt          # Python dependencies for producer.py    
│
├── consumer/           
│   ├── simple_consumer.py        # Reads messages from Kafka topic
│   ├── requirements.txt          # Python dependencies for consumer.py   
│   └── data_loader.py            # Loads consumed data into Postgres               
│
├── dashboard/
│   └── app.py                    # Streamlit dashboard for analytics
│
├── db/
│   └── init.sql                  # Database schema for transactions table
│
├── docker/
│   └── docker-compose.yml        # Container setup for Kafka, Postgres, pgAdmin
│
├── .env                          # Environment variables for container services
│
├── docs/
│   └── setup_instructions.md     # Detailed project setup and run instructions
│
└── README.md                     # Project overview (this file)
```
---

## 🚀 Planned Extensions

Future updates will introduce:

### 🔹 Spark Structured Streaming
To replace the basic Kafka consumer with a distributed stream processing engine capable of large-scale data ingestion, transformation, and real-time fraud analytics.

### 🔹 Machine Learning Model Integration
A predictive fraud detection layer trained on historical transaction data to identify high-risk patterns, such as anomalous transaction frequency, unusual time-of-day activity, or suspicious location behavior. The model will generate fraud risk scores for each transaction and flag potential threats in real time.

### 🔹 Full Dockerized Deployment
The current setup already containerizes Kafka, ZooKeeper, and Postgres. Future updates will extend Docker integration to include the producer, consumer, and Streamlit dashboard, enabling a single-command startup for the entire pipeline.


---

## 📘 Setup and Deployment

All detailed setup steps — including project structure, Docker setup, environment variables, and running each component — are documented here:

📂 **[docs/setup_instructions.md](./docs/setup_instructions.md)**

---

## 🧾 License

This project is publicly available for learning and demonstration purposes only.  
All rights are reserved — reuse, modification, or redistribution of any part of this codebase is **not permitted** without explicit permission from the author.


---

## ✨ Author

**Clara Nduka**  
_Data & Software Engineer_  
📫 [ndukaclara@gmail.com](mailto:ndukaclara@gmail.com)  
💼 [linkedin.com/in/clara-nduka](https://www.linkedin.com/in/clara-nduka)

