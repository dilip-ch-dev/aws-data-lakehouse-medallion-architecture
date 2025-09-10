variable "secrets_manager_gemini_key_arn" {
  description = "The ARN of the Secrets Manager secret for the Gemini API key."
  type        = string
  sensitive   = true # Marks this variable as sensitive
}

variable "glue_job_log_group_arn" {
  description = "The ARN of the CloudWatch log group for Glue job output."
  type        = string
}
variable "s3_bucket_name" {
  description = "The name of the S3 bucket for the data lake."
  type        = string
}