import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, StringType, LongType, DoubleType, ArrayType
from pyspark.sql.functions import col, from_json, to_timestamp


schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("session_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("product_category", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("details", StructType([
        StructField("amount", DoubleType(), True),
        StructField("payment_method", StringType(), True),
        StructField("items", ArrayType(StructType([
            StructField("product_id", StringType(), True),
            StructField("quantity", LongType(), True)
        ])), True)
    ]), True)
])

spark = SparkSession.builder \
    .appName("EcommerceLogConsumer") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:29092") \
    .option("subscribe", "LogEvents") \
    .option("startingOffsets", "latest") \
    .load()

par_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

print("Starting streaming query...")
query = par_df.writeStream \
    .format("json") \
    .option("path", "/logs") \
    .option("checkpointLocation", "checkpoint") \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .start()

query.awaitTermination()