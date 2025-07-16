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



print("Starting streaming queries...")

# Write to HDFS
query_hdfs = par_df.writeStream \
    .format("json") \
    .option("path", "hdfs://namenode:8020/event_data") \
    .option("checkpointLocation", "hdfs://namenode:8020/event_data/checkpoint") \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .start()


print("Both HDFS and Cassandra streaming queries started!")

# Wait for termination
query_hdfs.awaitTermination()
