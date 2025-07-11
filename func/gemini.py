from config import GEMINI_API_KEY
from wsgiref import types
from google import genai
from google.genai import types
from datetime import datetime

class GeminiYapper:

    GEMINI_API_KEY = GEMINI_API_KEY

    CONTEXT = "You are a helpful trip planning assistant built for EZtrip. " \
    "The current datetime is " + datetime.now().strftime("%Y-%m-%d") + ". " \
    "You are based in Singapore and can help users plan trips to various locations. " \
    "Your mission is to provide travel advice, suggest activities, and help users create itineraries. " \
    "Respond in plain sentences (max 3), no bullet points, no markdown, no asterisks, no emojis. " \
    "Be concise, avoid brand endorsements or price quotes. " \
    "If a request is vague, ask follow-up questions (max 2). " \
    "You may suggest a specific location for the trip. " \
    "Help the users plan a trip by suggesting ideas for things to do at their specific destination. Destination is "

    MODELS = [
        "gemini-2.5-flash-preview-05-20",
        "gemini-2.0-flash-001",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash-8b",
    ]

    def __init__(self):
        self.api_key = self.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key)
        available_models = self.client.models.list()
        available_model_names = [model.name for model in available_models]
        print("Starting GeminiYapper")
        print("Available models:", available_model_names)
        self.MODEL = self.MODELS[0]  
        

    def start(self, location):
        model = self.MODEL
        context = self.CONTEXT + location
        response = self.client.models.generate_content(
            model=model, 
            config=types.GenerateContentConfig(system_instruction=context),
            contents="Introduce yourself in 2 sentences, and how you can help the user with their trip to " + location + ". " \
        )
        return response.text

    def reply(self, chat_history, location):
        model = self.MODEL
        context = self.CONTEXT + location
        contents = []
        
        for msg in chat_history:
            role = "model" if msg["role"] == "assistant" else msg["role"]
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        response = self.client.models.generate_content(
            model=model, 
            config=types.GenerateContentConfig(system_instruction=context),
            contents=contents
        )
        return response.text

# TESTING ONLY
if __name__ == "__main__":
    planner = GeminiYapper()
    print(planner.start("Paris"))
    chat = [
        {"role": "user", "content": "Hi, can you help me plan a trip to Paris?"},
        {"role": "model", "content": "Of course! When are you planning to go?"},
        {"role": "user", "content": "Next month. And I can't wait to get incredible food! What do you recommend?"}
    ]
    print(planner.reply(chat, "Paris"))