# EMR Notebook (EMR Studio)
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("FraudDetection") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()

# Processamento similar, mas sem Feature Store nativo