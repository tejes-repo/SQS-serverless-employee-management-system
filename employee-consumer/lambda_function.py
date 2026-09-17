# ============================================================
# FILE: employee-consumer
#
# AWS Lambda
#
# SQS
#   ↓
# employee-consumer
#   ↓
# DynamoDB
#
# Handles:
#
# CREATE
# UPDATE
# DELETE
#
# DynamoDB Table:
# employees
#
# Partition Key:
# id (String)
# ============================================================


import json
import boto3


# ============================================================
# DYNAMODB RESOURCE
# ============================================================

dynamodb = boto3.resource(
    "dynamodb"
)


# ============================================================
# DYNAMODB TABLE
# ============================================================

table = dynamodb.Table(
    "employees"
)


# ============================================================
# MAIN LAMBDA HANDLER
# ============================================================

def lambda_handler(event, context):

    print("================================================")
    print("EMPLOYEE CONSUMER STARTED")
    print("================================================")


    # Print complete SQS event
    print("SQS EVENT:")

    print(
        json.dumps(event)
    )


    try:

        # ====================================================
        # PROCESS ALL SQS RECORDS
        # ====================================================

        records = event.get(
            "Records",
            []
        )


        print(
            "TOTAL SQS RECORDS:",
            len(records)
        )


        for record in records:


            print("------------------------------------------------")
            print("PROCESSING SQS RECORD")
            print("------------------------------------------------")


            # =================================================
            # GET SQS MESSAGE BODY
            # =================================================

            message_body = record.get(
                "body"
            )


            if not message_body:

                raise Exception(
                    "SQS message body is empty"
                )


            print("RAW SQS MESSAGE:")

            print(
                message_body
            )


            # =================================================
            # CONVERT JSON STRING TO DICTIONARY
            # =================================================

            employee = json.loads(
                message_body
            )


            print("PARSED EMPLOYEE MESSAGE:")

            print(
                json.dumps(employee)
            )


            # =================================================
            # GET OPERATION
            # =================================================

            operation = employee.get(
                "operation"
            )


            # =================================================
            # GET EMPLOYEE ID
            # =================================================

            employee_id = employee.get(
                "id"
            )


            print(
                "OPERATION:",
                operation
            )


            print(
                "EMPLOYEE ID:",
                employee_id
            )


            # =================================================
            # VALIDATE OPERATION
            # =================================================

            if not operation:

                raise Exception(
                    "Operation is missing from SQS message"
                )


            # =================================================
            # VALIDATE EMPLOYEE ID
            # =================================================

            if not employee_id:

                raise Exception(
                    "Employee ID is missing from SQS message"
                )


            # =================================================
            # CREATE OPERATION
            #
            # Producer sends:
            #
            # {
            #     "operation": "CREATE",
            #     "id": "...",
            #     "name": "...",
            #     "email": "...",
            #     "department": "..."
            # }
            # =================================================

            if operation == "CREATE":


                print(
                    "PROCESSING CREATE OPERATION"
                )


                # ------------------------------------------------
                # Validate CREATE fields
                # ------------------------------------------------

                if not employee.get(
                    "name"
                ):

                    raise Exception(
                        "Name is missing for CREATE"
                    )


                if not employee.get(
                    "email"
                ):

                    raise Exception(
                        "Email is missing for CREATE"
                    )


                if not employee.get(
                    "department"
                ):

                    raise Exception(
                        "Department is missing for CREATE"
                    )


                # ------------------------------------------------
                # Insert employee into DynamoDB
                # ------------------------------------------------

                table.put_item(

                    Item={

                        "id":
                            employee["id"],

                        "name":
                            employee["name"],

                        "email":
                            employee["email"],

                        "department":
                            employee["department"]

                    }

                )


                print(
                    "CREATE SUCCESS"
                )


                print(
                    "Employee created:",
                    employee_id
                )


            # =================================================
            # UPDATE OPERATION
            #
            # Producer sends:
            #
            # {
            #     "operation": "UPDATE",
            #     "id": "...",
            #     "name": "...",
            #     "email": "...",
            #     "department": "..."
            # }
            # =================================================

            elif operation == "UPDATE":


                print(
                    "PROCESSING UPDATE OPERATION"
                )


                # ------------------------------------------------
                # Validate UPDATE fields
                # ------------------------------------------------

                if not employee.get(
                    "name"
                ):

                    raise Exception(
                        "Name is missing for UPDATE"
                    )


                if not employee.get(
                    "email"
                ):

                    raise Exception(
                        "Email is missing for UPDATE"
                    )


                if not employee.get(
                    "department"
                ):

                    raise Exception(
                        "Department is missing for UPDATE"
                    )


                # ------------------------------------------------
                # Update DynamoDB item
                # ------------------------------------------------

                update_response = table.update_item(

                    Key={

                        "id":
                            employee["id"]

                    },


                    UpdateExpression="""
                        SET #employee_name = :name,
                            email = :email,
                            department = :department
                    """,


                    ExpressionAttributeNames={

                        "#employee_name":
                            "name"

                    },


                    ExpressionAttributeValues={

                        ":name":
                            employee["name"],

                        ":email":
                            employee["email"],

                        ":department":
                            employee["department"]

                    },


                    ReturnValues=
                        "ALL_NEW"

                )


                print(
                    "UPDATE SUCCESS"
                )


                print(
                    "Employee updated:",
                    employee_id
                )


                print(
                    "UPDATED ITEM:"
                )


                print(
                    json.dumps(
                        update_response.get(
                            "Attributes",
                            {}
                        )
                    )
                )


            # =================================================
            # DELETE OPERATION
            #
            # Producer sends:
            #
            # {
            #     "operation": "DELETE",
            #     "id": "..."
            # }
            # =================================================

            elif operation == "DELETE":


                print(
                    "PROCESSING DELETE OPERATION"
                )


                # ------------------------------------------------
                # Delete employee from DynamoDB
                # ------------------------------------------------

                delete_response = table.delete_item(

                    Key={

                        "id":
                            employee["id"]

                    },


                    ReturnValues=
                        "ALL_OLD"

                )


                # ------------------------------------------------
                # Check whether item existed
                # ------------------------------------------------

                deleted_item = delete_response.get(
                    "Attributes"
                )


                if deleted_item:

                    print(
                        "DELETE SUCCESS"
                    )


                    print(
                        "Employee deleted:",
                        employee_id
                    )

                else:

                    print(
                        "DELETE REQUEST PROCESSED"
                    )


                    print(
                        "Employee was not found:",
                        employee_id
                    )


            # =================================================
            # UNKNOWN OPERATION
            # =================================================

            else:


                print(
                    "UNKNOWN OPERATION:",
                    operation
                )


                raise Exception(
                    "Unknown operation: " +
                    str(operation)
                )


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:


        print("================================================")
        print("EMPLOYEE CONSUMER ERROR")
        print("================================================")


        print(
            str(e)
        )


        # ----------------------------------------------------
        # IMPORTANT
        #
        # Do NOT return success here.
        #
        # Raise the error so Lambda/SQS knows that
        # processing failed and can retry the message.
        # ----------------------------------------------------

        raise e


    # ========================================================
    # SUCCESS
    # ========================================================

    print("================================================")
    print("ALL SQS MESSAGES PROCESSED SUCCESSFULLY")
    print("================================================")


    return {

        "statusCode":
            200,

        "body":
            json.dumps({

                "message":
                    "SQS messages processed successfully"

            })

    }


# ============================================================
# AWS CONFIGURATION
# ============================================================


# Lambda Function:
#
# employee-consumer


# DynamoDB Table:
#
# employees


# Partition Key:
#
# id
#
# Type:
# String


# ============================================================
# SQS TRIGGER
# ============================================================
#
# SQS Queue:
#
# employee-queue
#
#       ↓
#
# employee-consumer
#
# Trigger:
# ENABLED
#
# ============================================================


# ============================================================
# IAM ROLE
# ============================================================
#
# employee-consumer Lambda execution role needs
# DynamoDB permissions.
#
# For learning/testing:
#
# AmazonDynamoDBFullAccess
#
#
# Better minimum permissions:
#
# dynamodb:PutItem
# dynamodb:UpdateItem
# dynamodb:DeleteItem
#
# ============================================================


# ============================================================
# MESSAGE 1 - CREATE
# ============================================================
#
# SQS message:
#
# {
#     "operation": "CREATE",
#     "id": "123",
#     "name": "Vikas",
#     "email": "vikas@gmail.com",
#     "department": "DevOps"
# }
#
# DynamoDB:
#
# put_item()
#
# ============================================================


# ============================================================
# MESSAGE 2 - UPDATE
# ============================================================
#
# SQS message:
#
# {
#     "operation": "UPDATE",
#     "id": "123",
#     "name": "Vikas Jagtap",
#     "email": "vikas.updated@gmail.com",
#     "department": "Cloud"
# }
#
# DynamoDB:
#
# update_item()
#
# ============================================================


# ============================================================
# MESSAGE 3 - DELETE
# ============================================================
#
# SQS message:
#
# {
#     "operation": "DELETE",
#     "id": "123"
# }
#
# DynamoDB:
#
# delete_item()
#
# ============================================================


# ============================================================
# FINAL FLOW
# ============================================================
#
# POST
#   ↓
# employee-producer
#   ↓
# SQS
#   ↓
# employee-consumer
#   ↓
# CREATE
#   ↓
# DynamoDB put_item()
#
#
# PUT
#   ↓
# employee-producer
#   ↓
# SQS
#   ↓
# employee-consumer
#   ↓
# UPDATE
#   ↓
# DynamoDB update_item()
#
#
# DELETE
#   ↓
# employee-producer
#   ↓
# SQS
#   ↓
# employee-consumer
#   ↓
# DELETE
#   ↓
# DynamoDB delete_item()
#
#
# GET
#   ↓
# get-employees
#   ↓
# DynamoDB scan()
#
# ============================================================
