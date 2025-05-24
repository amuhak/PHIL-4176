import azure.functions as func
import logging
import json

app = func.FunctionApp()

@app.function_name(name="HttpTrigger1")
@app.route(route="req")
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    response_data = {"reply": "Hello, bill!"}
    return func.HttpResponse(
        body=json.dumps(response_data),
        status_code=200,
        mimetype="application/json"
    )