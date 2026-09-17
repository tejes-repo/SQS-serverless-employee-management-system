# 🌟 AWS Serverless Employee Management System

[![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

An end-to-end **AWS Serverless Event-Driven Employee Management System** demonstrating modern, decoupled cloud architecture. The system supports full CRUD operations processed asynchronously via Amazon SQS and stored in DynamoDB, featuring a responsive frontend hosted on S3.

---

## 📐 Architecture Diagram

Below is the conceptual event-driven architecture design. The client interacts with API Gateway, which delegates write operations to an SQS queue via a Producer Lambda, while a Consumer Lambda processes the queue messages to update DynamoDB asynchronously. Read operations are handled directly.

![AWS Serverless Employee Management System Architecture](Architecture.webp)

### 🔄 System Workflow & Request Flow

```text
                  ┌──────────────────────────────┐
                  │      Amazon S3 Frontend      │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │     Amazon API Gateway       │
                  └──────┬────────────────┬──────┘
                         │ (GET)          │ (POST / PUT / DELETE)
                         ▼                ▼
     ┌───────────────────────┐        ┌───────────────────────┐
     │  get-employees Lambda │        │    producer Lambda    │
     └───────────┬───────────┘        └───────────┬───────────┘
                 │ (Scan)                         │ (SendMessage)
                 │                                ▼
                 │                    ┌───────────────────────┐
                 │                    │     Amazon SQS Queue  │
                 │                    └───────────┬───────────┘
                 │                                │ (Trigger)
                 │                                ▼
                 │                    ┌───────────────────────┐
                 │                    │  consumer Lambda      │
                 │                    └───────────┬───────────┘
                 │                                │ (Put/Update/Delete)
                 ▼                                ▼
     ┌────────────────────────────────────────────────────────┐
     │                  Amazon DynamoDB Table                 │
     └────────────────────────────────────────────────────────┘
```

---

## ⚡ Key Features

*   **Decoupled & Event-Driven**: Uses SQS to buffer and decouple write requests (`CREATE`, `UPDATE`, `DELETE`) from backend persistence, increasing fault tolerance.
*   **Asynchronous Message Processing**: Worker Lambda consumer automatically polls SQS messages and executes database modifications.
*   **Serverless CRUD Operations**: Full capability to create, read, update, and delete employees with no servers to manage.
*   **Highly Performant Frontend**: Static HTML/CSS/JS single-page application hosted on Amazon S3.
*   **Secure & Least-Privilege IAM**: Configured with minimal permission sets for each specific Lambda function.
*   **Monitoring & Observability**: Integrated with Amazon CloudWatch for live operational metrics and logging.

---

## 📂 Repository Structure

```text
SQS-serverless-employee-management-system/
│
├── employee-producer/
│   └── lambda_function.py      # Extracts API requests & publishes to SQS
│
├── employee-consumer/
│   └── lambda_function.py      # Consumes SQS messages & processes CRUD in DynamoDB
│
├── get-employees/
│   └── lambda_function.py      # Direct scanner of employee records in DynamoDB
│
├── frontend/
│   └── index.html              # Responsive Bootstrap-styled Dashboard UI
│
├── Architecture.png            # Visual Architecture Diagram
├── project.txt                 # Setup notes & reference codes
└── README.md                   # Project Documentation
```

---

## 🔗 CRUD API Specification

| Method | Endpoint | Lambda Target | DB Operation | Delivery Type |
| :--- | :--- | :--- | :--- | :--- |
| **POST** | `/register` | [`employee-producer`](file:///d:/aws/SQS-Lambda-s3-api%20gateway-db/employee-producer/lambda_function.py) | `CREATE` | Asynchronous (via SQS) |
| **GET** | `/employees` | [`get-employees`](file:///d:/aws/SQS-Lambda-s3-api%20gateway-db/get-employees/lambda_function.py) | `READ` | Synchronous |
| **PUT** | `/employees/{id}` | [`employee-producer`](file:///d:/aws/SQS-Lambda-s3-api%20gateway-db/employee-producer/lambda_function.py) | `UPDATE` | Asynchronous (via SQS) |
| **DELETE** | `/employees/{id}` | [`employee-producer`](file:///d:/aws/SQS-Lambda-s3-api%20gateway-db/employee-producer/lambda_function.py) | `DELETE` | Asynchronous (via SQS) |

---

## 🛠️ AWS Services & Configurations

### 1. Amazon DynamoDB
*   **Table Name**: `employees`
*   **Partition Key**: `id` (String / UUID)
*   **Attributes**: `id`, `name`, `email`, `department`

### 2. Amazon SQS
*   **Queue Name**: `employee-queue`
*   **Queue Type**: Standard Queue
*   **Retention Period**: Default (4 days)

### 3. API Gateway
*   **Protocol**: HTTP API
*   **CORS Configuration**:
    *   `Access-Control-Allow-Origin`: `*`
    *   `Access-Control-Allow-Headers`: `*`
    *   `Access-Control-Allow-Methods`: `GET, POST, PUT, DELETE, OPTIONS`

### 4. IAM Least-Privilege Policies

| Component | Required Actions | Resources |
| :--- | :--- | :--- |
| **employee-producer** | `sqs:SendMessage` | `arn:aws:sqs:<region>:<account-id>:employee-queue` |
| **employee-consumer** | `dynamodb:PutItem`, `dynamodb:UpdateItem`, `dynamodb:DeleteItem` | `arn:aws:dynamodb:<region>:<account-id>:table/employees` |
| **get-employees** | `dynamodb:Scan` | `arn:aws:dynamodb:<region>:<account-id>:table/employees` |

---

## 🚀 Setup & Deployment Guide

<details>
<summary><b>Click to Expand: Step-by-Step Deployment</b></summary>

### Step 1: Create DynamoDB Table
1. Go to AWS DynamoDB Console -> **Create Table**.
2. Table name: `employees`.
3. Partition key: `id` (Type: `String`).
4. Keep all other settings default and click **Create**.

### Step 2: Create SQS Queue
1. Go to Amazon SQS Console -> **Create Queue**.
2. Select **Standard** queue type.
3. Queue Name: `employee-queue`.
4. Keep default configuration parameters and click **Create Queue**.
5. Copy the **Queue URL** (e.g., `https://sqs.ap-south-1.amazonaws.com/<your-account-id>/employee-queue`).

### Step 3: Configure IAM Execution Role
1. Go to IAM Console -> **Roles** -> **Create Role**.
2. Select **AWS Service** -> **Lambda** as the trusted entity.
3. Attach standard permissions:
   * `AWSLambdaBasicExecutionRole` (for CloudWatch Logs)
   * Custom policy allowing `sqs:SendMessage` and DynamoDB CRUD (or `AmazonSQSFullAccess` and `AmazonDynamoDBFullAccess` for testing).
4. Save the role name (e.g., `employee-lambda-role`).

### Step 4: Deploy Lambda Functions
Create three Lambda functions using **Python 3.14 (or 3.x)** runtime:

1. **`employee-producer`**:
   * Deploy the code in [`employee-producer/lambda_function.py`](file:///d:/aws/SQS-Lambda-s3-api%20gateway-db/employee-producer/lambda_function.py).
   * In **Configuration** -> **Environment variables**, add:
     * Key: `QUEUE_URL`
     * Value: `<Your-SQS-Queue-URL>`
2. **`employee-consumer`**:
   * Deploy the code in [`employee-consumer/lambda_function.py`](file:///d:/aws/SQS-Lambda-s3-api%20gateway-db/employee-consumer/lambda_function.py).
   * Click **Add Trigger** -> Select **SQS** -> Select `employee-queue` -> Click **Add** to enable automatic SQS trigger.
3. **`get-employees`**:
   * Deploy the code in [`get-employees/lambda_function.py`](file:///d:/aws/SQS-Lambda-s3-api%20gateway-db/get-employees/lambda_function.py).

### Step 5: Setup API Gateway
1. Open API Gateway Console -> **Create API** -> Select **HTTP API** -> **Build**.
2. API Name: `employee-api`.
3. Configure the following Routes:
   * `POST /register` (Integration: `employee-producer`)
   * `GET /employees` (Integration: `get-employees`)
   * `PUT /employees/{id}` (Integration: `employee-producer`)
   * `DELETE /employees/{id}` (Integration: `employee-producer`)
4. Configure **CORS**:
   * Set Origin: `*`
   * Set Headers: `*`
   * Set Methods: `GET, POST, PUT, DELETE, OPTIONS`
5. Deploy the API to a stage (e.g., `prod`) and copy the generated **Invoke URL**.

### Step 6: Deploy S3 Frontend
1. Open [`frontend/index.html`](file:///d:/aws/SQS-Lambda-s3-api%20gateway-db/frontend/index.html) and replace the `API_URL` value (line 593) with your API Gateway Invoke URL.
2. Open S3 Console -> **Create Bucket**.
3. Enable **Static Website Hosting** in Properties.
4. Upload the modified `frontend/index.html`.
5. Set appropriate Bucket Policy for public read access (or access via CloudFront).
6. Open your S3 website endpoint URL in a web browser!
</details>

---

## 🛠️ Testing & Troubleshooting

<details>
<summary><b>Click to Expand: Payload Formats & Debugging Tips</b></summary>

### Sample SQS / Payload Messages

#### CREATE
```json
{
  "operation": "CREATE",
  "id": "27d04e5d-c6a6-48be-8f64-42f0a149f1db",
  "name": "Vikas Jagtap",
  "email": "vikas@gmail.com",
  "department": "DevOps"
}
```

#### UPDATE
```json
{
  "operation": "UPDATE",
  "id": "27d04e5d-c6a6-48be-8f64-42f0a149f1db",
  "name": "Vikas Prakash Jagtap",
  "email": "vikasjagtap@gmail.com",
  "department": "Cloud"
}
```

#### DELETE
```json
{
  "operation": "DELETE",
  "id": "27d04e5d-c6a6-48be-8f64-42f0a149f1db"
}
```

### Common Issues & Troubleshooting

*   **`PUT` or `DELETE` returns 404 (Not Found)**:
    *   Verify the API Gateway route pattern is exact: `/employees/{id}`.
    *   Ensure the HTTP methods `PUT` and `DELETE` are integrated with the `employee-producer` Lambda.
    *   Verify you deployed the API changes.
*   **`CORS` / Failed to Fetch Errors**:
    *   Ensure CORS is configured on the API Gateway with all headers allowed (`*`), origin allowed (`*`), and methods set to `GET, POST, PUT, DELETE, OPTIONS`.
    *   Don't forget to deploy the API to your active stage (`prod`) after changing CORS configuration.
*   **SQS Queue Messages Not Processed**:
    *   Check if the **SQS Trigger** on `employee-consumer` Lambda is enabled.
    *   Inspect CloudWatch Logs for the `employee-consumer` function to verify database operations.
*   **To inspect SQS messages manually**:
    1. Temporarily disable the SQS trigger on `employee-consumer` Lambda.
    2. Perform an action on the UI (Add, Update, or Delete).
    3. Visit the SQS Console, choose your queue, click **Send and receive messages**, and click **Poll for messages**.
    4. You will see the raw JSON messages waiting in the queue.
    5. Re-enable the trigger; they will be immediately processed.
</details>

---

## 👨‍💻 About the Author

### **P TEJESWAR REDDY**
*🎓 B.TECH. Computer Science Student*

*   **Primary Interests**: Cloud Computing, Amazon Web Services (AWS), DevOps Engineering, Serverless Architectures, and Backend Development.
*   **Goal**: Building scalable, resilient, and cost-effective cloud-native systems.
*   **Connect**: Feel free to reach out to collaborate on AWS / serverless projects!

---

## 📋 Project Status

| Component | Status | Component | Status |
| :--- | :--- | :--- | :--- |
| **Frontend UI** | ✅ Complete | **POST `/register`** | ✅ Complete |
| **GET `/employees`** | ✅ Complete | **PUT `/employees/{id}`** | ✅ Complete |
| **DELETE `/employees/{id}`** | ✅ Complete | **API Gateway Routes** | ✅ Complete |
| **CORS Config** | ✅ Complete | **Lambda Producer** | ✅ Complete |
| **Lambda Consumer** | ✅ Complete | **SQS Queue Integration** | ✅ Complete |
| **DynamoDB Schema** | ✅ Complete | **S3 Static Website** | ✅ Complete |
| **IAM Configuration** | ✅ Complete | **Architecture Diagram** | ✅ Complete |
