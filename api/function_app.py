import azure.functions as func
import logging
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="req")
def req(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Attempt to get JSON from the request body
        body_dict = req.get_json()
    except ValueError:
        # This catches:
        # 1. Empty request body
        # 2. Non-JSON content type
        # 3. Malformed JSON
        # 4. JSON that is not an object (e.g., "null", "[]", "123")
        logging.error("Failed to parse JSON body or body is empty/invalid.")
        return func.HttpResponse(
             "Please pass a valid JSON object in the request body.",
             status_code=400
        )

    logging.info(f"Received parameters (as dict): {body_dict}")

    # Check if the parsed JSON object is empty (e.g., {})
    if not body_dict: # This handles the case where the body was "{}"
        return func.HttpResponse(
             "Request body was an empty JSON object. Please provide key-value pairs (e.g., {\"name\": \"Azure\"})",
             status_code=400
        )

    response_data = {"reply": body_dict}
    return func.HttpResponse(
        body=json.dumps(response_data),
        status_code=200,
        mimetype="application/json"
    )