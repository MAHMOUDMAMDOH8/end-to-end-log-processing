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
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "LogEvents") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

par_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Flatten the DataFrame for Cassandra (Cassandra doesn't support nested objects)
print(par_df.printSchema())
flat_df = par_df.select(
    par_df["timestamp"],
    par_df["level"],
    par_df["service"],
    par_df["event_type"],
    par_df["user_id"],
    par_df["session_id"],
    par_df["product_id"],
    par_df["session_duration"],
    par_df["device_type"],
    par_df["geo_location.country"].alias("geo_country"),
    par_df["geo_location.city"].alias("geo_city"),
    par_df["details.amount"].alias("details_amount"),
    par_df["details.payment_method"].alias("details_payment_method"),
    par_df["details.items"].alias("details_items"),
    par_df["details.order_id"].alias("details_order_id"),
    par_df["details.query"].alias("details_query"),
    par_df["details.results_count"].alias("details_results_count"),
    par_df["details.shipping_method"].alias("details_shipping_method"),
    par_df["details.delivery_estimate"].alias("details_delivery_estimate"),
    par_df["details.completed_at"].alias("details_completed_at"),
    par_df["details.shipping_address"].alias("details_shipping_address"),
    par_df["details.attempted_amount"].alias("attempted_amount"),
    par_df["details.failed_at"].alias("failed_at"),
    par_df["error_code"],
    par_df["message"],
    par_df["error_at"]
    
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