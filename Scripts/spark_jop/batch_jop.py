from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, ArrayType
import sys
from pyspark.sql.functions import col, to_json
import os

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Batch Job") \
    .getOrCreate()

# Define schema
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

# Read all JSON files from HDFS directory
hdfs_path = "hdfs://namenode:8020/event_data/*.json"

print(f"Reading all JSON files from HDFS path: {hdfs_path}")
try:
    df = spark.read.schema(schema).option("multiline", "false").json(hdfs_path)
    total_rows = df.count()
    print(f"Total rows in all files: {total_rows}")
    if total_rows == 0:
        print("No data found in the JSON files.")
        spark.stop()
        sys.exit(0)
except Exception as e:
    print(f"Error reading files: {e}")
    spark.stop()
    sys.exit(1)



# --- Split and flatten logs by category ---

# 1. Search Response


search_df = df[df["event_type"] == "search"].select(
    "timestamp", "level" , "service", "event_type" , "user_id" , "session_id" ,"product_id" , 
    "session_duration" , "device_type" ,  df["geo_location.country"].alias("geo_country"),
    df["geo_location.city"].alias("geo_city"),
    df["details.query"].alias("query"),
    df["details.results_count"].alias("results_count")
)



# 2. Error Response
error_df = df[df["event_type"] == "error"].select(
    "timestamp", "level" , "service", "event_type" , "user_id" , "session_id" ,"product_id" , 
    "session_duration" , "device_type" ,  df["geo_location.country"].alias("geo_country"),
    df["geo_location.city"].alias("geo_city"),
    df["error_code"].alias("error_code"),
    df["message"].alias("message"),
    df["error_at"].alias("error_at")
)



# 3. Order Complete Response
order_complete_df = df[df["event_type"] == "order_complete"].select(
    "timestamp", "level" , "service", "event_type" , "user_id" , "session_id" ,"product_id" , 
    "session_duration" , "device_type" ,  df["geo_location.country"].alias("geo_country"),
    df["geo_location.city"].alias("geo_city"),
    df["details.amount"].alias("amount"),
    df["details.shipping_address"].alias("shipping_address"),
    df["details.items.quantity"].alias("quantity"),
    df["details.order_id"].alias("order_id"),
    df["details.shipping_method"].alias("shipping_method"),
    df["details.delivery_estimate"].alias("delivery_estimate"),
    df["details.completed_at"].alias("completed_at")

)

# 4. Purchase Response
purchase_df = df[df["event_type"] == "purchase"].select(
    "timestamp", "level" , "service", "event_type" , "user_id" , "session_id" ,"product_id" , 
    "session_duration" , "device_type" ,  df["geo_location.country"].alias("geo_country"),
    df["geo_location.city"].alias("geo_city"),
    df["details.amount"].alias("amount"),
    df["details.payment_method"].alias("payment_method"),
    df["details.items.quantity"].alias("quantity"),
    df["details.shipping_address"].alias("shipping_address")
)



# 5. order_failed
order_failed_df = df[df["event_type"] == "order_failed"].select(
    "timestamp", "level" , "service", "event_type" , "user_id" , "session_id" ,"product_id" , 
    "session_duration" , "device_type" ,  df["geo_location.country"].alias("geo_country"),
    df["geo_location.city"].alias("geo_city"),
    df["details.order_id"].alias("order_id"),
    df["details.attempted_amount"].alias("attempted_amount"),
    df["details.failed_at"].alias("failed_at")
)
# --- Write each DataFrame to its own table ---

# Write to postgres
# TODO: For production, use environment variables or a config file for DB credentials
# Example:
# import os
# db_params = {
#     "host": os.environ.get("PG_HOST"),
#     "port": os.environ.get("PG_PORT"),
#     "database": os.environ.get("PG_DATABASE"),
#     "user": os.environ.get("PG_USER"),
#     "password": os.environ.get("PG_PASSWORD")
# }
db_params = {
    "host": "aws-0-eu-west-3.pooler.supabase.com",
    "port": 6543,
    "database": "postgres",
    "user": "postgres.vrxamhmisrlwxnykimqx",
    "password": "logs123+"
}

search_df.write.format("jdbc")\
    .option("url", f"jdbc:postgresql://{db_params['host']}:{db_params['port']}/{db_params['database']}?prepareThreshold=0")\
    .option("dbtable", "search_response")\
    .option("user", db_params["user"])\
    .option("password", db_params["password"])\
    .option("driver", "org.postgresql.Driver")\
    .mode("append")\
    .save()

error_df.write.format("jdbc")\
    .option("url", f"jdbc:postgresql://{db_params['host']}:{db_params['port']}/{db_params['database']}?prepareThreshold=0")\
    .option("dbtable", "error_response")\
    .option("user", db_params["user"])\
    .option("password", db_params["password"])\
    .option("driver", "org.postgresql.Driver")\
    .mode("append")\
    .save()

order_complete_df.write.format("jdbc")\
    .option("url", f"jdbc:postgresql://{db_params['host']}:{db_params['port']}/{db_params['database']}?prepareThreshold=0")\
    .option("dbtable", "order_complete_response")\
    .option("user", db_params["user"])\
    .option("password", db_params["password"])\
    .option("driver", "org.postgresql.Driver")\
    .mode("append")\
    .save()

purchase_df.write.format("jdbc")\
    .option("url", f"jdbc:postgresql://{db_params['host']}:{db_params['port']}/{db_params['database']}?prepareThreshold=0")\
    .option("dbtable", "purchase_response")\
    .option("user", db_params["user"])\
    .option("password", db_params["password"])\
    .option("driver", "org.postgresql.Driver")\
    .mode("append")\
    .save()

order_failed_df.write.format("jdbc")\
    .option("url", f"jdbc:postgresql://{db_params['host']}:{db_params['port']}/{db_params['database']}?prepareThreshold=0")\
    .option("dbtable", "order_failed_response")\
    .option("user", db_params["user"])\
    .option("password", db_params["password"])\
    .option("driver", "org.postgresql.Driver")\
    .mode("append")\
    .save()

print("Data written to postgres successfully")

# Archiving step (manual or via Hadoop API)
print("\nTo archive processed files, run this from the namenode container:")

os.system("hdfs dfs -mv /event_data/*.json /archive/")

spark.stop()








