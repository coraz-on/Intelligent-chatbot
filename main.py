import requests
import json
import nltk
from nltk.chat.util import Chat, reflections
from chatterbot import ChatBot
from rasa.nlu.model import Interpreter
from fastapi import FastAPI

# Initialize NLTK for chatbot functionality
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Initialize Rasa NLU interpreter
interpreter = Interpreter.load("path/to/nlu/model")

# Initialize user context
user_context = {}

# Create rule-based and machine learning-based chatbots
def create_chatbots():
    rule_based_chatbot = Chat([
        ("my name is (.*)", ["Hello %1!", "Hi %1!"]),
        ("(hi|hello|hey)", ["Hello!", "Hi there!"]),
        ("how are you?", ["I'm good, thank you!", "I'm fine, thanks!"]),
        ("(bye|goodbye)", ["Goodbye!", "See you later!"]),
    ], reflections)
    
    machine_learning_chatbot = ChatBot('MyBot')
    trainer = ChatterBotCorpusTrainer(machine_learning_chatbot)
    trainer.train('chatterbot.corpus.english')
    
    return rule_based_chatbot, machine_learning_chatbot

# Handle backend system integration
def call_backend_system(intent, user_input):
    api_url = "https://your-backend-api.com/api/intent"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "intent": intent,
        "user_input": user_input,
        "context": user_context
    }
    
    response = requests.post(api_url, data=json.dumps(payload), headers=headers)
    data = response.json()
    
    return data["response"]

# Initialize FastAPI
app = FastAPI()

# Define API endpoint for chatbot interaction
@app.post("/chat")
async def chat_with_bot(message: str):
    rasa_response = interpreter.parse(message)
    intent = rasa_response["intent"]["name"]
    
    rule_based_chatbot, machine_learning_chatbot = create_chatbots()
    
    rule_response = rule_based_chatbot.respond(message)
    if rule_response:
        return {"response": rule_response}
    
    ml_response = machine_learning_chatbot.get_response(message)
    
    backend_response = call_backend_system(intent, message)
    user_context.update(backend_response.get("context", {}))
    
    return {"response": ml_response, "backend_response": backend_response["response"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
