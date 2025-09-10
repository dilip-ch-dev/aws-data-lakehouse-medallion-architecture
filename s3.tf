# Unique name for S3 bucket
resource "aws_s3_bucket" "taxi_data_lake" {
  bucket = var.s3_bucket_name

  tags = {
    Name = "NYC Taxi Data Lake"
  }
}