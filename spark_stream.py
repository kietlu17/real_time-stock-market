from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, FloatType, LongType

# Tạo SparkSession
def create_spark_session():
    return SparkSession.builder \
        .appName("KafkaToPostgres") \
        .getOrCreate()

# Đọc dữ liệu từ Kafka
def read_from_kafka(spark, kafka_bootstrap_servers, topics):
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", topics) \
        .load() \
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# Định dạng schema cho dữ liệu
def process_data(df):
    schema = StructType([
        StructField("symbol", StringType()),
        StructField("timestamp", StringType()),
        StructField("open", FloatType()),
        StructField("high", FloatType()),
        StructField("low", FloatType()),
        StructField("close", FloatType()),
        StructField("volume", LongType())
    ])
    
    return df.withColumn("value", from_json(col("value"), schema)).select(col("value.*"))

# Ghi dữ liệu vào PostgreSQL
def write_to_postgres(df, db_url, db_table, db_properties):
    return df.writeStream \
        .format("jdbc") \
        .option("url", db_url) \
        .option("dbtable", db_table) \
        .options(**db_properties) \
        .outputMode("append") \
        .start()

if __name__ == "__main__":
    # Bước 1: Tạo SparkSession
    spark = create_spark_session()

    # Bước 2: Đọc dữ liệu từ Kafka
    kafka_bootstrap_servers = "broker:29092"  # Địa chỉ Kafka broker
    topics = "AAPL,AMD,AMZN"  # Các topic Kafka
    df = read_from_kafka(spark, kafka_bootstrap_servers, topics)

    # Bước 3: Xử lý dữ liệu
    processed_df = process_data(df)

    # Bước 4: Ghi dữ liệu vào PostgreSQL
    db_url = "jdbc:postgresql://postgres:5432/stock_market"  # Địa chỉ của PostgreSQL
    db_table = "stock_prices"  # Tên bảng trong PostgreSQL
    db_properties = {
        "user": "airflow",  # Tên người dùng PostgreSQL
        "password": "airflow",  # Mật khẩu PostgreSQL
        "driver": "org.postgresql.Driver"  # Driver PostgreSQL
    }
    write_query = write_to_postgres(processed_df, db_url, db_table, db_properties)

    # Chờ cho đến khi quá trình hoàn thành
    write_query.awaitTermination()
