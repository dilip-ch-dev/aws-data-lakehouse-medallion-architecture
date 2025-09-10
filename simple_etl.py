import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Get job parameters and arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'INPUT_BUCKET', 'OUTPUT_BUCKET'])
job_name = args['JOB_NAME']
input_bucket = args['INPUT_BUCKET']
output_bucket = args['OUTPUT_BUCKET']

print(f"Starting Glue job: {job_name}")
print(f"Reading from S3 bucket: {input_bucket}")
print(f"Writing to S3 bucket: {output_bucket}")

# Get a reference to the Spark Context and Glue Context
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Initialize the job with the provided arguments
job.init(args['JOB_NAME'], args)

# Defining input and output paths using the passed arguments
input_path = f"s3://{input_bucket}/raw/sample_data.csv"
output_path = f"s3://{output_bucket}/processed/processed_data.csv"

# Reads the raw data (will manually upload a file to S3 later)
try:
    print(f"Reading data from: {input_path}")
    raw_data = spark.read.csv(input_path, header=True, inferSchema=True)
    print("Successfully read data.")
except Exception as e:
    print(f"Error reading data from {input_path}: {e}")
    sys.exit(1)

# A simple transformation: adding a new column
processed_data = raw_data.withColumn("new_column", raw_data["passenger_count"] + 1)
print("Transformation complete. New column 'new_column' added.")

# Write the processed data to the processed folder
try:
    print(f"Writing processed data to: {output_path}")
    processed_data.write.csv(output_path, mode="overwrite")
    print("Successfully wrote processed data.")
except Exception as e:
    print(f"Error writing data to {output_path}: {e}")
    sys.exit(1)

job.commit()
