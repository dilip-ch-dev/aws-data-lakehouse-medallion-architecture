# aws-data-lakehouse-medallion-architecture
An end-to-end data pipeline on AWS using a Medallion Architecture with Glue, Athena, and Terraform.
# AWS Data Lakehouse with Medallion Architecture

## Project Overview

This project demonstrates the design and implementation of a complete, end-to-end data pipeline on AWS. The solution leverages a **Medallion Architecture** (Bronze, Silver, Gold layers) to process data from a raw, unstructured text file into a final, business-ready dataset. The entire infrastructure is provisioned as code using **Terraform**.

## Architecture Diagram



The pipeline is structured as follows:

* **Bronze Layer:** Raw data is ingested from a source (e.g., S3) and stored in its original format.
* **Silver Layer:** Data is cleaned, standardized, and conformed. An advanced ETL job interacts with an external API (Google Gemini) to transform unstructured text into structured, semi-structured data.
* **Gold Layer:** Final, aggregated data is created for business intelligence and analytics. This layer is optimized for fast querying with services like Amazon Athena.

## Technical Stack

* **Cloud Provider:** Amazon Web Services (AWS)
* **Infrastructure as Code:** Terraform
* **Data Storage:** AWS S3
* **ETL & Orchestration:** AWS Glue
* **Query Engine:** Amazon Athena
* **External API:** Google Gemini API
* **Programming Language:** Python

## Key Achievements

* **Implemented a complete end-to-end data pipeline** from raw data ingestion to business-ready reporting.
* **Provisioned all AWS infrastructure** (data lake, S3 buckets, Glue jobs, etc.) using **Terraform**, demonstrating proficiency in IaC and reproducible deployments.
* **Engineered an advanced ETL job** that used a large language model (LLM) to extract structured insights from unstructured text.
* **Successfully transformed and validated data** through each layer of the medallion architecture, ensuring data quality and reliability.

## Project Files

This repository contains the following files:

* `terraform/`: Terraform code for provisioning the AWS infrastructure.
* `glue_scripts/`: Python scripts for the Glue ETL jobs.
* `README.md`: This project overview.
