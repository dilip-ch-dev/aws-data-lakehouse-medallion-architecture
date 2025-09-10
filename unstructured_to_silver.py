import sys
import json
import boto3
import os
import google.api_core.exceptions as api_exceptions
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import lit, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import google.generativeai as genai

# Function to securely retrieve the secret from Secrets Manager
def get_secret(secret_name):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        raise Exception(f"Failed to retrieve secret '{secret_name}': {e}")
    else:
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])
        else:
            return get_secret_value_response['SecretBinary']

# Get job parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'INPUT_BUCKET', 'OUTPUT_BUCKET', 'SECRETS_ARN'])
input_bucket = args['INPUT_BUCKET']
output_bucket = args['OUTPUT_BUCKET']
secrets_arn = args['SECRETS_ARN']

# Get API key securely
secrets = get_secret(secrets_arn)
gemini_api_key = secrets['GEMINI_API_KEY']

# Configure the Gemini API client
genai.configure(api_key=gemini_api_key)
client = genai.GenerativeModel('gemini-1.5-flash')

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read the raw text file from the Bronze layer
raw_text_rdd = sc.textFile(f"s3://{input_bucket}/bronze/unstructured/raw_text_data.txt")
raw_text = "".join(raw_text_rdd.collect())

print("--- START DEBUG ---")
print(f"Raw text from S3 (first 200 chars): {raw_text[:200]}")

# Define the structured schema we want to extract
schema = StructType([
    StructField("topic", StringType(), True),
    StructField("sentiment", StringType(), True),
    StructField("summary", StringType(), True)
])

# Use LLM to extract structured data
try:
    print("Calling Gemini API to extract structured data...")
    response = client.generate_content(
        f"""
        You are a helpful assistant that extracts information from text and returns it as a JSON object.

        **Instructions:**
        1. Read the provided text.
        2. Extract the topic, sentiment, and a one-sentence summary.
        3. Return only a single JSON object. Do not include any extra words, explanations, or formatting outside of the JSON.

        **Example JSON format:**
        ```json
        {{
          "topic": "your_topic_here",
          "sentiment": "your_sentiment_here",
          "summary": "your_summary_here"
        }}
        ```

        **Text to analyze:**
        {raw_text}
        """
    )
    
    print(f"API response object received: {response}")
    print(f"Type of response object: {type(response)}")
    
    # --- fix: Remove markdown code fences and clean the string ---
    json_output_str = response.text.strip()
    
    if json_output_str.startswith("```json"):
        json_output_str = json_output_str.replace("```json", "", 1)
    if json_output_str.endswith("```"):
        json_output_str = json_output_str.replace("```", "", 1)
    
    json_output_str = json_output_str.strip()
    # --- End of the fix ---
    
    print(f"Value of response.text after cleaning: '{json_output_str}'")
    
    if json_output_str:
        print("Successfully extracted structured data from the LLM.")
        
        extracted_data = json.loads(json_output_str)
        extracted_df = spark.createDataFrame([extracted_data], schema=schema)
        
        print("Structured DataFrame:")
        extracted_df.show(truncate=False)
        
        output_path = f"s3://{output_bucket}/silver/unstructured/"
        extracted_df.write.parquet(output_path, mode="overwrite")
        
        print("Successfully wrote structured data to the Silver layer.")
    else:
        print("Warning: Gemini API returned an empty or invalid response. Skipping data processing.")
        
except api_exceptions.GoogleAPIError as e:
    print(f"Google API Error occurred: {e}")
    raise
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    raise

print("--- END DEBUG ---")
job.commit()