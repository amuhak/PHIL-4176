import azure.functions as func
import logging
app = func.FunctionApp()

@app.function_name(name="HttpTrigger1")
@app.route(route="req")
def main(req: func.HttpRequest) -> str:
    logging.info('Python HTTP trigger function processed a request.')
    return f"Hello, bill!"