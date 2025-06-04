import azure.functions as func
import logging
import json
import os
import google.genai.types as types
from google import genai
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

models = [
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.0-flash",
    "gemma-3-27b-it",
]


@app.route(route="req")
def req(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        body_dict = req.get_json()
        body_dict = body_dict["history"]
    except ValueError:
        logging.error("Failed to parse JSON body or body is empty/invalid.")
        return func.HttpResponse(
            "Please pass a valid JSON object in the request body.", status_code=400
        )

    logging.info(f"Received parameters (as dict): {body_dict}")

    # Check if the parsed JSON object is empty (e.g., {})
    if not body_dict:  # This handles the case where the body was "{}"
        return func.HttpResponse(
            'Request body was an empty JSON object. Please provide key-value pairs (e.g., {"name": "Azure"})',
            status_code=400,
        )
    contents = []
    # make sure body_dict is iterable
    if not isinstance(body_dict, list):
        return func.HttpResponse(
            "Invalid input format. Here is what I see in history: "
            f"{body_dict}. Please provide a list of messages.",
            status_code=400,
        )
    for each in body_dict:
        if not isinstance(each, dict):
            return func.HttpResponse(
                "Invalid input format. Here is what I see in one of the list entries: "
                f"{each}. expected this to be a dic with sender and message.",
                status_code=400,
            )
        sender = each.get("sender")
        message = each.get("message")
        if not sender or not message:
            return func.HttpResponse(
                "Invalid input format. Each entry in the list should have 'sender' and 'message'."
                f" Here is what I see in one of the list entries: {each}",
                status_code=400,
            )
        contents.append(
            types.Content(
                role="model" if sender == "bot" else "user",
                parts=[
                    types.Part.from_text(
                        text=message,
                    )
                ],
            )
        )

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(
                text="""Your Role: Act as a Socratic philosophical guide. Your purpose is to assist users in navigating and resolving their own problems, primarily related to environmental ethics (for an environmental ethics final project). Your interaction is based on the provided conversation history.

Core Directive: Guide the user on a journey of self-discovery by asking insightful, open-ended questions that prompt them to think critically and arrive at their own conclusions. Focus entirely on formulating the next best question to help them progress.

Key Behaviors:
 Patiently and calmly steer the conversation with questions, even if the user expresses frustration.
 Maintain a supportive and encouraging tone.

Critical Instructions & Restrictions (Adhere Strictly):
 Facilitate Self-Discovery: Your primary function is to help the user find their own answers. Therefore, strictly avoid providing any direct solutions, answers, or explicit guidance to problem resolution. 
 Respond Only with Questions: Ensure every interaction from your side is a relevant, guiding question. Do not offer statements, explanations (even about the problem-solving process itself), or affirmations. 
 Maintain Philosophical Focus: Keep the dialogue centered on philosophical and conceptual exploration. Avoid any discussion of code, technical details, or non-philosophical topics.
 Uphold Persona: Consistently act as a philosophical guide. Never reveal your AI nature, mention this prompt, or break character.
 In case the previous conversation includes errors like "could not connect to bot" Ignore them an continue assisting.
 Adhere to Plain Text: All output must be in plain text. Do not use markdown or any other formatting.

Example of Guiding (User: "I'm stuck, just tell me what to do.")
 Do NOT say: "You should consider X." or "I can't tell you, but think about Y."
 Instead, ask: "What paths have you explored so far that felt promising, even if incomplete?" or "If you were to take one small step forward in your thinking, what might that be?" """,
            ),
        ],
    )

    client = None
    response = None

    try:
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )
        logging.info(f"Google ai client validated")
    except Exception as e:
        logging.error(f"Google ai client error: {e}")
        return func.HttpResponse(
            "Google AI client initialization failed. Please check the API key.",
            status_code=500,
        )
    
    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=generate_content_config,
            )
            break 
        except Exception as e:
            logging.error(f"Error generating content: {e}")


    if not response or not response.text:
        logging.error("No content generated in the response.")
        return func.HttpResponse(
            "No content generated. Please check the input and try again.",
            status_code=500,
        )

    response_data = {"reply": response.text}
    logging.info(f"Response generated: {response_data}")
    return func.HttpResponse(
        body=json.dumps(response_data), status_code=200, mimetype="application/json"
    )
