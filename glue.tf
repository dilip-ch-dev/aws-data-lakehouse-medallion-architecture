# IAM Role for AWS Glue
resource "aws_iam_role" "glue_role" {
  name = "glue-etl-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      },
    ]
  })
}

# Attaching permissions to the IAM role for S3, Glue, and Secrets Manager
resource "aws_iam_role_policy" "glue_policy" {
  name = "glue-policy"
  role = aws_iam_role.glue_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ],
        Resource = [
          aws_s3_bucket.taxi_data_lake.arn,
          "${aws_s3_bucket.taxi_data_lake.arn}/*"
        ]
      },
      {
        Effect   = "Allow",
        Action   = "secretsmanager:GetSecretValue",
        Resource = var.secrets_manager_gemini_key_arn # <-- UPDATED
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = var.glue_job_log_group_arn # <-- UPDATED
      },
      {
        Effect   = "Allow"
        Action   = [
          "glue:*",
          "iam:PassRole",
          "ec2:CreateNetworkInterface",
          "ec2:DeleteNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
      }
    ]
  })
}

# The PySpark script for the Bronze-to-Silver ETL
resource "aws_s3_object" "bronze_to_silver_script" {
  bucket      = aws_s3_bucket.taxi_data_lake.id
  key         = "scripts/bronze_to_silver.py"
  source      = "./bronze_to_silver.py"
  source_hash = filemd5("./bronze_to_silver.py")
}

# AWS Glue Job for the Bronze-to-Silver ETL
resource "aws_glue_job" "bronze_to_silver_job" {
  name     = "bronze-to-silver-job"
  role_arn = aws_iam_role.glue_role.arn

  command {
    script_location = "s3://${aws_s3_bucket.taxi_data_lake.id}/${aws_s3_object.bronze_to_silver_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--INPUT_BUCKET"      = aws_s3_bucket.taxi_data_lake.id
    "--OUTPUT_BUCKET"     = aws_s3_bucket.taxi_data_lake.id
    "--TempDir"           = "s3://${aws_s3_bucket.taxi_data_lake.id}/temp/"
    "--job-bookmark-option" = "job-bookmark-disable"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
}

# The PySpark script for the Silver-to-Gold ETL
resource "aws_s3_object" "silver_to_gold_script" {
  bucket      = aws_s3_bucket.taxi_data_lake.id
  key         = "scripts/silver_to_gold.py"
  source      = "./silver_to_gold.py"
  source_hash = filemd5("./silver_to_gold.py")
}

# AWS Glue Job for the Silver-to-Gold ETL
resource "aws_glue_job" "silver_to_gold_job" {
  name     = "silver-to-gold-job"
  role_arn = aws_iam_role.glue_role.arn

  command {
    script_location = "s3://${aws_s3_bucket.taxi_data_lake.id}/${aws_s3_object.silver_to_gold_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--INPUT_BUCKET"      = aws_s3_bucket.taxi_data_lake.id
    "--OUTPUT_BUCKET"     = aws_s3_bucket.taxi_data_lake.id
    "--TempDir"           = "s3://${aws_s3_bucket.taxi_data_lake.id}/temp/"
    "--job-bookmark-option" = "job-bookmark-disable"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
}

# The PySpark script for the Unstructured-to-Silver ETL
resource "aws_s3_object" "unstructured_to_silver_script" {
  bucket      = aws_s3_bucket.taxi_data_lake.id
  key         = "scripts/unstructured_to_silver.py"
  source      = "./unstructured_to_silver.py"
  source_hash = filemd5("./unstructured_to_silver.py")
}

# AWS Glue Job for the Unstructured-to-Silver ETL
resource "aws_glue_job" "unstructured_to_silver_job" {
  name     = "unstructured-to-silver-job"
  role_arn = aws_iam_role.glue_role.arn

  command {
    script_location = "s3://${aws_s3_bucket.taxi_data_lake.id}/${aws_s3_object.unstructured_to_silver_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--INPUT_BUCKET"              = aws_s3_bucket.taxi_data_lake.id
    "--OUTPUT_BUCKET"             = aws_s3_bucket.taxi_data_lake.id
    "--SECRETS_ARN"               = var.secrets_manager_gemini_key_arn # <-- UPDATED
    "--TempDir"                   = "s3://${aws_s3_bucket.taxi_data_lake.id}/temp/"
    "--job-bookmark-option"       = "job-bookmark-disable"
    "--additional-python-modules" = "google-generativeai"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
}