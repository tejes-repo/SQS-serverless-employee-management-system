# ============================================================
# Lambda Function: employee-producer
#
# Handles:
#
# POST   /register
# PUT    /employees/{id}
# DELETE /employees/{id}
#
# Flow:
#
# API Gateway
#      ↓
# employee-producer
#      ↓
# SQS employee-queue
#      ↓
# employee-consumer
#      ↓
# DynamoDB employees
# ============================================================


import json
import boto3
import uuid
import os
import base64


# ============================================================
# SQS CLIENT
# ============================================================

sqs = boto3.client("sqs")


# ============================================================
# SQS QUEUE URL
# ============================================================

QUEUE_URL = os.environ["QUEUE_URL"]


# ============================================================
# LAMBDA HANDLER
# ============================================================

def lambda_handler(event, context):

    print("==========================================")
    print("EMPLOYEE PRODUCER STARTED")
    print("==========================================")


    # Print complete API Gateway event
    print("EVENT:")
    print(json.dumps(event))


    try:

        # ====================================================
        # GET HTTP METHOD
        # ====================================================

        method = (
            event
            .get("requestContext", {})
            .get("http", {})
            .get("method", "")
            .upper()
        )


        print("HTTP METHOD:", method)


        # ====================================================
        # GET PATH PARAMETERS
        #
        # PUT:
        # /employees/{id}
        #
        # DELETE:
        # /employees/{id}
        # ====================================================

        path_parameters = (
            event.get("pathParameters") or {}
        )


        employee_id = path_parameters.get(
            "id"
        )


        print(
            "EMPLOYEE ID:",
            employee_id
        )


        # ====================================================
        # GET REQUEST BODY
        # ====================================================

        body = {}


        raw_body = event.get(
            "body"
        )


        if raw_body:

            # ------------------------------------------------
            # Decode Base64 body if API Gateway sends it
            # ------------------------------------------------

            if event.get(
                "isBase64Encoded",
                False
            ):

                raw_body = base64.b64decode(
                    raw_body
                ).decode("utf-8")


            body = json.loads(
                raw_body
            )


        print("REQUEST BODY:")

        print(
            json.dumps(body)
        )


        # ====================================================
        # POST
        #
        # CREATE EMPLOYEE
        #
        # POST /register
        # ====================================================

        if method == "POST":

            print(
                "PROCESSING CREATE"
            )


            # ------------------------------------------------
            # Get fields
            # ------------------------------------------------

            name = body.get(
                "name"
            )


            email = body.get(
                "email"
            )


            department = body.get(
                "department"
            )


            # ------------------------------------------------
            # Validate name
            # ------------------------------------------------

            if not name:

                return api_response(

                    400,

                    {
                        "message":
                            "Name is required"
                    }

                )


            # ------------------------------------------------
            # Validate email
            # ------------------------------------------------

            if not email:

                return api_response(

                    400,

                    {
                        "message":
                            "Email is required"
                    }

                )


            # ------------------------------------------------
            # Validate department
            # ------------------------------------------------

            if not department:

                return api_response(

                    400,

                    {
                        "message":
                            "Department is required"
                    }

                )


            # ------------------------------------------------
            # CREATE MESSAGE
            # ------------------------------------------------

            employee = {

                "operation":
                    "CREATE",

                "id":
                    str(uuid.uuid4()),

                "name":
                    name,

                "email":
                    email,

                "department":
                    department

            }


        # ====================================================
        # PUT
        #
        # UPDATE EMPLOYEE
        #
        # PUT /employees/{id}
        # ====================================================

        elif method == "PUT":

            print(
                "PROCESSING UPDATE"
            )


            # ------------------------------------------------
            # Check ID
            # ------------------------------------------------

            if not employee_id:

                return api_response(

                    400,

                    {
                        "message":
                            "Employee ID is required"
                    }

                )


            # ------------------------------------------------
            # Get fields
            # ------------------------------------------------

            name = body.get(
                "name"
            )


            email = body.get(
                "email"
            )


            department = body.get(
                "department"
            )


            # ------------------------------------------------
            # Validate fields
            # ------------------------------------------------

            if not name:

                return api_response(

                    400,

                    {
                        "message":
                            "Name is required"
                    }

                )


            if not email:

                return api_response(

                    400,

                    {
                        "message":
                            "Email is required"
                    }

                )


            if not department:

                return api_response(

                    400,

                    {
                        "message":
                            "Department is required"
                    }

                )


            # ------------------------------------------------
            # UPDATE MESSAGE
            # ------------------------------------------------

            employee = {

                "operation":
                    "UPDATE",

                "id":
                    employee_id,

                "name":
                    name,

                "email":
                    email,

                "department":
                    department

            }


        # ====================================================
        # DELETE
        #
        # DELETE EMPLOYEE
        #
        # DELETE /employees/{id}
        # ====================================================

        elif method == "DELETE":

            print(
                "PROCESSING DELETE"
            )


            # ------------------------------------------------
            # Check ID
            # ------------------------------------------------

            if not employee_id:

                return api_response(

                    400,

                    {
                        "message":
                            "Employee ID is required"
                    }

                )


            # ------------------------------------------------
            # DELETE MESSAGE
            # ------------------------------------------------

            employee = {

                "operation":
                    "DELETE",

                "id":
                    employee_id

            }


        # ====================================================
        # OPTIONS
        #
        # Browser CORS preflight
        # ====================================================

        elif method == "OPTIONS":

            return api_response(

                200,

                {
                    "message":
                        "CORS OK"
                }

            )


        # ====================================================
        # INVALID METHOD
        # ====================================================

        else:

            return api_response(

                405,

                {

                    "message":
                        "Method not allowed",

                    "method":
                        method

                }

            )


        # ====================================================
        # PRINT FINAL MESSAGE
        # ====================================================

        print("==========================================")
        print("MESSAGE TO SQS")
        print("==========================================")


        print(
            json.dumps(employee)
        )


        # ====================================================
        # SEND MESSAGE TO SQS
        # ====================================================

        sqs_result = sqs.send_message(

            QueueUrl=QUEUE_URL,

            MessageBody=json.dumps(
                employee
            )

        )


        # ====================================================
        # SQS MESSAGE ID
        # ====================================================

        message_id = sqs_result.get(
            "MessageId"
        )


        print(
            "SQS MESSAGE ID:",
            message_id
        )


        print("==========================================")
        print("REQUEST SENT TO SQS SUCCESSFULLY")
        print("==========================================")


        # ====================================================
        # RETURN SUCCESS
        # ====================================================

        return api_response(

            200,

            {

                "message":
                    "Employee request sent to SQS",

                "operation":
                    employee["operation"],

                "id":
                    employee["id"],

                "sqsMessageId":
                    message_id

            }

        )


    # ========================================================
    # JSON ERROR
    # ========================================================

    except json.JSONDecodeError as e:

        print(
            "JSON DECODE ERROR:",
            str(e)
        )


        return api_response(

            400,

            {

                "message":
                    "Invalid JSON request body",

                "error":
                    str(e)

            }

        )


    # ========================================================
    # GENERAL ERROR
    # ========================================================

    except Exception as e:

        print(
            "PRODUCER ERROR:",
            str(e)
        )


        return api_response(

            500,

            {

                "message":
                    "Internal Server Error",

                "error":
                    str(e)

            }

        )



# ============================================================
# API RESPONSE FUNCTION
# ============================================================

def api_response(
    status_code,
    body
):

    return {

        "statusCode":
            status_code,

        "headers": {

            "Content-Type":
                "application/json",

            "Access-Control-Allow-Origin":
                "*",

            "Access-Control-Allow-Headers":
                "*",

            "Access-Control-Allow-Methods":
                "GET,POST,PUT,DELETE,OPTIONS"

        },

        "body":
            json.dumps(
                body
            )

    }


# ============================================================
# ENVIRONMENT VARIABLE
# ============================================================
#
# Lambda → employee-producer
# → Configuration
# → Environment variables
#
# Name:
#
# QUEUE_URL
#
# Value:
#
# https://sqs.ap-south-1.amazonaws.com/289857919920/employee-queue
#
# Use your actual Queue URL if different.
#
# ============================================================


# ============================================================
# API GATEWAY INTEGRATION
# ============================================================
#
# POST:
#
# POST /register
#       ↓
# employee-producer
#
#
# PUT:
#
# PUT /employees/{id}
#       ↓
# employee-producer
#
#
# DELETE:
#
# DELETE /employees/{id}
#       ↓
# employee-producer
#
# ============================================================


# ============================================================
# EXAMPLE POST MESSAGE
# ============================================================
#
# {
#     "operation": "CREATE",
#     "id": "generated-uuid",
#     "name": "Vikas",
#     "email": "vikas@gmail.com",
#     "department": "DevOps"
# }
#
# ============================================================


# ============================================================
# EXAMPLE PUT MESSAGE
# ============================================================
#
# PUT /employees/123
#
# {
#     "operation": "UPDATE",
#     "id": "123",
#     "name": "Vikas Jagtap",
#     "email": "vikas@gmail.com",
#     "department": "Cloud"
# }
#
# ============================================================


# ============================================================
# EXAMPLE DELETE MESSAGE
# ============================================================
#
# DELETE /employees/123
#
# {
#     "operation": "DELETE",
#     "id": "123"
# }
#
# ============================================================
