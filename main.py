from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import datetime
import json

app = Flask(__name__)

data_file = 'user_data.json'

def load_data():
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg = request.form.get('Body').strip().lower()
    user = request.form.get('From')
    response = MessagingResponse()
    reply = response.message()

    data = load_data()
    user_data = data.get(user, {"tasks": [], "reflections": []})

    if "start day" in msg:
        reply.body("Great! What are your top 3 tasks for today?")
        user_data['state'] = 'awaiting_tasks'
    elif user_data.get('state') == 'awaiting_tasks':
        user_data['tasks'].append({"date": str(datetime.date.today()), "tasks": msg})
        reply.body("Tasks saved! Type 'zone' to start your focus session.")
        user_data['state'] = ''
    elif "zone" in msg:
        reply.body("Focus session started for 60 minutes. I’ll check in later!")
    elif "reflect" in msg:
        reply.body("What are you proud of today?")
        user_data['state'] = 'awaiting_reflection'
    elif user_data.get('state') == 'awaiting_reflection':
        user_data['reflections'].append({"date": str(datetime.date.today()), "reflection": msg})
        reply.body("Reflection saved. Keep going strong.")
        user_data['state'] = ''
    else:
        reply.body("Hi! Type 'start day', 'zone', or 'reflect' to begin.")

    data[user] = user_data
    save_data(data)
    return str(response)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))