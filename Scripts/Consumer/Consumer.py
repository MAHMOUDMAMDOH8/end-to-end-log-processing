from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, StringType, LongType, DoubleType, ArrayType
from pyspark.sql.functions import col, from_json, to_json

hdfs_path = "hdfs://namenode:9000/event_data"

schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("level", StringType(), True),
    StructField("service", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("session_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("session_duration", LongType(), True),
    StructField("device_type", StringType(), True),
    StructField("geo_location", StructType([
        StructField("country", StringType(), True),
        StructField("city", StringType(), True)
    ]), True),
    StructField("details", StructType([
        StructField("amount", DoubleType(), True),
        StructField("payment_method", StringType(), True),
        StructField("items", ArrayType(StructType([
            StructField("product_id", StringType(), True),
            StructField("quantity", LongType(), True)
        ])), True),
        StructField("order_id", StringType(), True),
        StructField("query", StringType(), True),
        StructField("results_count", LongType(), True),
        StructField("shipping_method", StringType(), True),
        StructField("delivery_estimate", StringType(), True),
        StructField("completed_at", StringType(), True),
        StructField("shipping_address", StringType(), True),
        StructField("attempted_amount", DoubleType(), True),
        StructField("failed_at", StringType(), True)
    ]), True),
    StructField("error_code", StringType(), True),
    StructField("message", StringType(), True),
    StructField("error_at", StringType(), True)
])

spark = SparkSession.builder \
    .appName("EcommerceLogConsumer") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0") \
    .config("spark.cassandra.connection.host", "cassandra") \
    .config("spark.cassandra.connection.port", "9042") \
    .getOrCreate()

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "172.19.0.8:9092") \
    .option("subscribe", "LogEvents") \
    .option("startingOffsets", "latest") \
    .load()

par_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Flatten the DataFrame for Cassandra (Cassandra doesn't support nested objects)
flat_df = par_df.select(
    col("timestamp"),
    col("level"),
    col("service"),
    col("event_type"),
    col("user_id"),
    col("session_id"),
    col("product_id"),
    col("session_duration"),
    col("device_type"),
    col("geo_location.country").alias("geo_country"),
    col("geo_location.city").alias("geo_city"),
    col("details.amount").alias("details_amount"),
    col("details.payment_method").alias("details_payment_method"),
    to_json(col("details.items")).alias("details_items"),
    col("details.order_id").alias("details_order_id"),
    col("details.query").alias("details_query"),
    col("details.results_count").alias("details_results_count"),
    col("details.shipping_method").alias("details_shipping_method"),
    col("details.delivery_estimate").alias("details_delivery_estimate"),
    col("details.completed_at").alias("details_completed_at"),
    col("details.shipping_address").alias("details_shipping_address"),
    col("details.attempted_amount").alias("attempted_amount"),
    col("details.failed_at").alias("failed_at"),
    col("error_code"),
    col("message"),
    col("error_at")
)

print("Starting streaming queries...")

# Write to HDFS
query_hdfs = par_df.writeStream \
    .format("json") \
    .option("path", "hdfs://namenode:8020/event_data") \
    .option("checkpointLocation", "hdfs://namenode:8020/event_data/checkpoint") \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .start()

# Write to Cassandra
query_cassandra = flat_df.writeStream \
    .format("org.apache.spark.sql.cassandra") \
    .option("keyspace", "logs") \
    .option("table", "ecomm_log") \
    .option("checkpointLocation", "hdfs://namenode:8020/event_data/cassandra_checkpoint") \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .start()

print("Both HDFS and Cassandra streaming queries started!")

# Wait for termination
query_hdfs.awaitTermination()
query_cassandra.awaitTermination()