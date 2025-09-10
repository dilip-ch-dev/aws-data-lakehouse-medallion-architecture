# End-to-End Serverless Data Lakehouse on AWS

## 🚀 Project Goal

This project builds a complete, end-to-end, serverless data platform on AWS to process the NYC Taxi dataset. The primary goal is to demonstrate a modern, scalable, and cost-effective data engineering solution using the **Medallion Architecture** (Bronze, Silver, Gold layers). A key feature is the integration of a Large Language Model (Google Gemini) to process and structure unstructured text data.

---

## 🏛️ Architecture

The entire infrastructure is provisioned using **Terraform** for an Infrastructure-as-Code (IaC) approach. The data flows through the following stages:

1.  **Ingestion:** Raw structured (`.csv`) and unstructured (`.txt`) data is ingested into an S3 bucket, our data lake foundation.
2.  **Bronze Layer:** Raw, unaltered data is stored in the `bronze` layer of the S3 bucket.
3.  **Silver Layer:** An **AWS Glue** ETL job triggers to clean, transform, and structure the data.
    * For unstructured data, the Glue job calls the **Google Gemini API** (via AWS Secrets Manager) to perform entity extraction and convert text into a structured format.
    * The processed data is stored in the `silver` layer in a query-optimized format like Parquet.
4.  **Gold Layer:** A final AWS Glue job aggregates the silver-layer data into business-ready tables (e.g., for analytics or reporting) and stores it in the `gold` layer.
5.  **Consumption:** The final, business-ready data in the gold layer is exposed via **Amazon Athena**, allowing for easy querying using standard SQL.



---

## 🛠️ Tech Stack

* **Cloud Provider:** AWS
* **Infrastructure as Code:** Terraform
* **Data Lake:** AWS S3
* **ETL:** AWS Glue
* **Serverless Compute:** AWS Lambda (Implicit in Glue)
* **Secrets Management:** AWS Secrets Manager
* **AI/LLM:** Google Gemini API
* **Data Querying:** Amazon Athena
* **Core Language:** Python (PySpark)

---

## ✨ Key Features

* **Fully Serverless:** No servers to manage, resulting in a cost-effective and scalable solution.
* **Medallion Architecture:** A best-practice architecture that ensures data quality and traceability.
* **LLM Integration:** Demonstrates cutting-edge ability to extract value from unstructured text data using an external AI service.
* **Infrastructure as Code:** The entire platform can be deployed and destroyed reliably using Terraform.

---

## ⚙️ Setup & Usage

To deploy this project in your own AWS account, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/dilip-ch-dev/aws-data-lakehouse-medallion-architecture.git](https://github.com/dilip-ch-dev/aws-data-lakehouse-medallion-architecture.git)
    cd aws-data-lakehouse-medallion-architecture
    ```
2.  **Configure AWS Credentials:** Ensure your AWS CLI is configured with the necessary permissions.
3.  **Prepare Terraform Variables:** Create a `terraform.tfvars` file in the root directory and provide values for the variables defined in `variables.tf`.
    ```
    # Example terraform.tfvars
    s3_bucket_name                 = "your-unique-s3-bucket-name"
    secrets_manager_gemini_key_arn = "your-secrets-manager-arn"
    glue_job_log_group_arn         = "your-log-group-arn"
    ```
4.  **Deploy the Infrastructure:**
    ```bash
    terraform init
    terraform apply
    ```
5.  **Trigger the Pipeline:** Upload data to the `bronze` folder in your newly created S3 bucket to start the ETL process.
