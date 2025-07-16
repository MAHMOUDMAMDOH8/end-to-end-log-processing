# End-to-End Log Processing System

## Overview

This project is an end-to-end big data pipeline for processing, storing, and analyzing e-commerce event logs. It leverages modern data engineering tools and technologies, including:

- **Kafka** for real-time event streaming
- **Spark Structured Streaming** for real-time data processing
- **HDFS** for distributed storage
- **Cassandra** for scalable NoSQL storage and analytics
- **PostgreSQL** for analytics-ready storage
- **dbt** for data transformation and modeling
- **Airflow** for workflow orchestration (including batch jobs)
- **Docker Compose** for easy multi-service orchestration
- **Streamlit** for real-time monitoring and visualization
- **Power BI** for business intelligence and visualization

## Architecture Diagram

```mermaid
graph TD
    A[📊 Log Generator] --> B[🔄 Kafka]
    B --> C[⚡ Spark Structured Streaming]
    C --> D[📈 Cassandra<br/>Real-time Store]
    D --> E[📊 Streamlit<br/>Real-time Monitoring]
    C --> F[🗄️ HDFS<br/>Raw Log Storage]
    F --> G[🛠️ Airflow Batch Job]
    G --> H[📊 PostgreSQL<br/>Analytics DB]
    H --> I[🔄 dbt Models]
    I --> J[📈 Power BI<br/>Business Reports]
```

## Real-Time Monitoring Dashboard

Our system includes comprehensive real-time monitoring capabilities through Streamlit:

![Real-time Events Dashboard](Monitoring/Real-time%20Events.png)
*Real-time events dashboard showing live event ingestion, filtering, and inspection*

![Geographic Analysis Dashboard](Monitoring/Geographic%20Analysis.png)
*Geographic analysis dashboard visualizing user activity by location*

![Pipeline Monitoring Dashboard](Monitoring/Pipeline%20Monitoring.png)
*Pipeline monitoring dashboard displaying system health, event flow, and error rates*

## Pipeline Monitoring with Streamlit

You can also monitor your pipeline using the interactive Streamlit dashboard, which provides:
- Real-time event ingestion and error rates
- Detailed log inspection and filtering
- Event type breakdowns and timelines
- Geographic and real-time event analysis

### To run the Streamlit dashboard:

```bash
pip install streamlit plotly pandas numpy
streamlit run streamlit_dashboard.py
```

- The dashboard will be available at [http://localhost:8501](http://localhost:8501) by default.
- Use this dashboard for operational monitoring and log inspection.

## Analytics & Statistics Dashboard

Advanced analytics and statistical insights are available through our dedicated analytics dashboard:

![Statistics Analytics Dashboard](Monitoring/STATISTICS_ANALYTICS.png)

*Comprehensive analytics dashboard displaying key business metrics, user behavior patterns, and performance statistics*

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant LG as Log Generator
    participant K as Kafka
    participant SS as Spark Streaming
    participant C as Cassandra
    participant H as HDFS
    participant A as Airflow
    participant P as PostgreSQL
    participant G as Streamlit
    participant PB as Power BI

    LG->>K: Send log events
    K->>SS: Stream events
    SS->>C: Store processed data
    SS->>H: Store raw logs
    C->>G: Real-time metrics
    H->>A: Trigger batch job
    A->>P: Load analytics data
    P->>PB: Business reports
```

## Directory Structure

```
end-to-end-log-processing/
├── Scripts/
│   ├── produser/
│   │   ├── Producer.py          # Kafka producer for log events
│   │   ├── logs.py              # Log generator logic
│   │   ├── users.json           # Sample user data
│   │   └── products.json        # Sample product data
│   ├── Consumer/
│   │   └── Consumer.py          # Spark Structured Streaming consumer
│   └── spark_jop/
│       └── batch_jop.py         # Batch processing job
├── Monitoring/
│   ├── EVENTMONITORING.png      # Event monitoring dashboard
│   ├── STATISTICS_ANALYTICS.png # Analytics dashboard
├── dags/                        # Airflow DAGs
├── dbt/                         # dbt project for transformations
├── cassandra_setup.cql          # Cassandra schema setup
├── setup_cassandra.sh           # Cassandra initialization script
├── docker-compose.yaml          # Multi-service orchestration
└── dockerfile                   # Custom Docker build for Airflow
```

## Codebase Index

### Top-Level Structure

- **Scripts/**
  - **produser/**
    - `Producer.py`: Kafka producer for log events
    - `logs.py`: Log generator logic
    - `users.json`, `products.json`: Sample data
  - **Consumer/**
    - `Consumer.py`: Spark Structured Streaming consumer (reads from Kafka, writes to HDFS & Cassandra)
  - **spark_jop/**
    - `batch_jop.py`: Spark batch job (reads from HDFS, writes to PostgreSQL)
- **dags/**
  - `batch_job_dag.py`: Airflow DAG for orchestrating batch Spark job and dbt runs
- **dbt/**
  - **Ecommerce_model/**: Main dbt project
    - `dbt_project.yml`: dbt project config
    - `models/`: dbt models
      - `staging/`: Staging models (STG_user.sql, STG_Event.sql, STG_orders.sql, STG_Products.sql)
      - `olap_model/`: OLAP models
        - `fact/`: Fact tables (Fact_order.sql, Fact_Event.sql)
        - `dimensions/`: Dimension tables (Dim_users.sql, Dim_product.sql, Dim_date.sql)
      - `source.yml`: Source table definitions
    - `snapshots/`: Snapshots (CDC_product.sql)
    - `seeds/`, `tests/`, `analyses/`, `macros/`, `dbt_packages/`, `logs/`: dbt project structure
    - `README.md`: dbt project readme
- **Monitoring/**
  - `streamlit_dashboard.py`: Streamlit dashboard for real-time monitoring
  - Dashboard images: EVENTMONITORING.png, STATISTICS_ANALYTICS.png, Real-time Events.png, Geographic Analysis.png, Pipeline Monitoring.png
- **cassandra_setup.cql**: Cassandra schema setup
- **setup_cassandra.sh**: Cassandra initialization script
- **docker-compose.yaml**: Multi-service orchestration
- **dockerfile**: Custom Docker build for Airflow
- **logs/**: Airflow and pipeline logs
- **hadoop/**: Hadoop binaries (if any)
- **plugins/**, **includes/**: Airflow plugins and includes

---

## dbt Lineage & Data Model

The dbt project models the analytics layer in PostgreSQL, transforming raw event data into business-ready fact and dimension tables. The lineage below shows the flow from raw sources to final models:

![dbt Lineage](image/dbt.png)
*dbt lineage graph: sources → staging → facts/dimensions → analytics*

- **Sources**: Raw tables loaded from Spark batch job (e.g., `order_complete_response`, `search_response`, etc.)
- **Staging Models**: Clean and standardize raw data (`STG_user`, `STG_Event`, `STG_orders`, `STG_Products`)
- **Snapshots**: Track slowly changing dimensions (e.g., `CDC_product`)
- **Fact Tables**: Event and order facts (`Fact_Event`, `Fact_order`)
- **Dimension Tables**: User, product, and date dimensions (`Dim_users`, `Dim_product`, `Dim_date`)

See `dbt/Ecommerce_model/models/` for full SQL logic and model details.

## Prerequisites

- Docker & Docker Compose
- Python 3.8+ (for running scripts outside containers, if needed)
- Power BI Desktop (for analytics)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/MAHMOUDMAMDOH8/end-to-end-log-processing
cd end-to-end-log-processing
```

### 2. Start the System

```bash
docker-compose up -d
```

This will start all required services: Kafka, Zookeeper, Spark, HDFS (NameNode/DataNode), Cassandra, Airflow, PostgreSQL, Streamlit, and more.

### 3. Initialize Cassandra

After the containers are up, set up the Cassandra keyspace and table:

```bash
bash setup_cassandra.sh
```

This runs the schema in `cassandra_setup.cql` and verifies the setup.

### 4. Produce Log Events

In a new terminal, run the producer to generate and send events to Kafka:

```bash
docker exec -it spark bash
cd /opt/spark/scripts/produser
python3 Producer.py
```

### 5. Start the Consumer

In another terminal, run the Spark consumer to process and store the events:

```bash
docker exec -it spark bash
cd /opt/spark/scripts/Consumer
python3 Consumer.py
```

### 6. Monitor Real-Time Data

Access the Streamlit dashboard for real-time, interactive, log-focused monitoring:

**Streamlit UI**: [http://localhost:8501](http://localhost:8501)

### 7. Batch Processing: HDFS to PostgreSQL (Every 10 Minutes)

Airflow is configured to run a DAG every 10 minutes that:
- Reads new data from HDFS
- Loads it into PostgreSQL for analytics

You can find and customize the DAG in `dags/spark_batch_job_dag.py`.

**Airflow UI**: [http://localhost:8082](http://localhost:8082)
- Username: `airflow`
- Password: `airflow`

### 8. Data Transformation with dbt

After data lands in PostgreSQL, dbt is used for data modeling and transformation. The dbt project is located in the `dbt/` directory.

To run dbt transformations:

```bash
docker exec -it <airflow-or-dbt-container> bash
cd /opt/airflow/dbt
# Configure your dbt profile for PostgreSQL connection
# Then run:
dbt run
```

### 9. Analytics with Power BI

- Connect Power BI Desktop to the PostgreSQL database (host: `localhost`, port: `5432`, user: `airflow`, password: `airflow`, db: `airflow`).
- Build dashboards and reports on top of the dbt models.

### 10. Accessing the Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Spark UI** | [http://localhost:8080](http://localhost:8080) | - |
| **HDFS NameNode UI** | [http://localhost:9870](http://localhost:9870) | - |
| **Streamlit** | [http://localhost:8501](http://localhost:8501) | - |
| **Airflow UI** | [http://localhost:8082](http://localhost:8082) | airflow/airflow |
| **Cassandra** | Port 9042 | - |
| **PostgreSQL** | Port 5432 | airflow/airflow |
| **Kafka** | Port 9092 (internal), 29092 (external) | - |

## Data Flow

1. **📊 Producer** generates logs and sends them to Kafka topic `LogEvents`.
2. **⚡ Consumer** reads from Kafka, parses and flattens the data, writes raw logs to HDFS and processed logs to Cassandra.
3. **📈 Streamlit** provides real-time monitoring and visualization of the streaming data.
4. **🛠️ Airflow** runs a batch job every 10 minutes to move new data from HDFS to PostgreSQL.
5. **🔄 dbt** transforms and models the data in PostgreSQL.
6. **📊 Power BI** connects to PostgreSQL for analytics and visualization.
7. **📈 Cassandra** table `logs.ecomm_log` is indexed for fast queries on event type, user, product, etc.

## Monitoring & Analytics Features

### Real-Time Monitoring
- **Event Count Tracking**: Monitor events by type, user, and geographic location
- **Performance Metrics**: Track processing latency and throughput
- **Error Monitoring**: Real-time alerting for system issues
- **Geographic Visualization**: World map showing user activity by country

### Statistical Analytics
- **User Behavior Analysis**: Session duration, product interactions
- **Revenue Tracking**: Purchase amounts, payment methods
- **Search Analytics**: Query patterns, result counts
- **Error Analysis**: Error codes, failure rates

### Dashboard Features
- **Real-time Updates**: Live data refresh every few seconds
- **Interactive Filters**: Drill-down capabilities by time, region, event type
- **Customizable Alerts**: Configure thresholds for automated notifications
- **Export Capabilities**: Download reports and data for further analysis

## Cassandra Table Schema

See `cassandra_setup.cql` for full schema. Main fields include:

- `timestamp`, `user_id`, `session_id`, `product_id`, `event_type`, `level`, `service`, etc.
- Flattened details for amounts, payment, shipping, errors, etc.

## Customization

- **Log Generation**: Edit `Scripts/produser/logs.py` to change event types, user/product pools, or log structure.
- **Consumer Logic**: Edit `Scripts/Consumer/Consumer.py` to change processing, filtering, or output logic.
- **Batch DAG**: Edit `dags/spark_batch_job_dag.py` to customize the batch ETL logic.
- **dbt Models**: Edit the `dbt/` project for custom transformations.

## Stopping the System

```bash
docker-compose down
```

## Troubleshooting

- Ensure all containers are healthy (`docker ps`).
- Check logs for each service (`docker logs <container>`).
- If Cassandra or PostgreSQL is not ready, wait a minute before running the setup script.

## Performance Optimization

- **Kafka**: Adjust partition count and replication factor based on throughput requirements
- **Spark**: Configure executor memory and cores based on data volume
- **Cassandra**: Optimize table design and indexing for your query patterns
- **PostgreSQL**: Configure connection pooling and query optimization

## Security Considerations

- Change default passwords in production
- Use SSL/TLS for database connections
- Implement proper network segmentation
- Regular security updates for all components

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 