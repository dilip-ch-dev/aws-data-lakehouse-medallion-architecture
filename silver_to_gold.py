import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, count

# Get job parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'INPUT_BUCKET', 'OUTPUT_BUCKET'])
input_bucket = args['INPUT_BUCKET']
output_bucket = args['OUTPUT_BUCKET']

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Reads the structured data from the Silver layer
silver_path = f"s3://{input_bucket}/silver/unstructured/"
silver_df = spark.read.parquet(silver_path)

print("Reading from Silver layer:")
silver_df.show(truncate=False)

# Group by topic and sentiment, then count each
gold_df = silver_df.groupBy("topic", "sentiment").agg(count("*").alias("sentiment_count"))

print("Writing to Gold layer (aggregated data):")
gold_df.show(truncate=False)

# Write the aggregated data to the Gold layer
gold_path = f"s3://{output_bucket}/gold/unstructured_insights/"
gold_df.write.parquet(gold_path, mode="overwrite")

print("Successfully wrote aggregated data to the Gold layer.")

job.commit()