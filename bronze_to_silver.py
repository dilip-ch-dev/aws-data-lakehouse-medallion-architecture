import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Get job parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'INPUT_BUCKET', 'OUTPUT_BUCKET'])
input_bucket = args['INPUT_BUCKET']
output_bucket = args['OUTPUT_BUCKET']

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read from the raw (Bronze) layer
input_path = f"s3://{input_bucket}/raw/"
raw_df = spark.read.csv(input_path, header=True, inferSchema=True)
print(f"Read {raw_df.count()} rows from the Bronze layer.")

# Transformation: Filter out records with zero passengers
silver_df = raw_df.filter(raw_df.passenger_count > 0)
print(f"Filtered to {silver_df.count()} rows for the Silver layer.")

# Write to the Silver layer in Parquet format
output_path = f"s3://{output_bucket}/silver/"
silver_df.write.parquet(output_path, mode="overwrite")
print("Successfully wrote data to the Silver layer.")

job.commit()