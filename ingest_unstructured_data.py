import requests
from bs4 import BeautifulSoup
import boto3
import os

def ingest_and_upload_to_s3(url, bucket_name, s3_key):
    """
    Fetches a web page's text and uploads it directly to an S3 bucket.
    """
    print(f"Fetching data from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        raw_text = soup.get_text()
        clean_text = "\n".join([line for line in raw_text.splitlines() if line.strip()])

        # Using boto3 to upload the text to S3
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=clean_text)

        print(f"Successfully uploaded raw text to s3://{bucket_name}/{s3_key}")

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")

if __name__ == "__main__":
    # Get S3 bucket name from an environment variable (best practice)
    bucket_name = os.getenv("S3_BUCKET")
    if not bucket_name:
        print("S3_BUCKET environment variable not set. Please set it to your bucket name.")
    else:
        # Bronze layer for unstructured data
        s3_key = "bronze/unstructured/raw_text_data.txt"
        target_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        ingest_and_upload_to_s3(target_url, bucket_name, s3_key)