import os
from dotenv import load_dotenv
load_dotenv()
from src import db,ngrok,scraper,chatGLM
from flask import Flask, render_template, request,make_response
import uuid
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ['SECRET_KEY']

p_flag = os.environ['PRODUCTION'] == "True"

# Update base URLs to use the public ngrok URL in production
if p_flag:
    app.config["BASE_URL"] = ngrok.open_tunnel()
    app.debug = False
else:
    app.debug = True

# Create an instance of ProductionChatGLM with p_flag=True
glm = chatGLM.chatGLM(p_flag=p_flag)
socketio = SocketIO(app)
db_conn = db.connect_to_mongodb()


collection = db_conn['chats']

chat_schema = {
    'chat_id': '',
    'messages': [],
}
message_schema = {
        'message_id':'',
        'user_query': '',
        'bot_response': '',
}



def generate_unique_id():
    return str(uuid.uuid4())

@socketio.on("connect")
def on_connect():
    # Generate a unique room name based on the client's session ID
    room = request.sid
    emit("connected",{"sid":room},room=room)

@app.route("/")
def homepage():
    response = make_response(render_template("index.html"))
    return response
    

@app.route("/c/<chat_id>")
def chat_page(chat_id):
    response = make_response(render_template("index.html"))
    return response

@app.route('/fetch-chat', methods=['POST'])
def fetch_chat():
    data = request.json
    chat_id = data["chat_id"]
    chat_history = list(collection.find({'chat_id': chat_id}))
    print("chat history : ",chat_history)
    del chat_history[0]['_id']

    # Return the JSON data as bytes
    return chat_history[0]

@app.route('/send-message', methods=['POST'])
def send_message():
    def generate_response():
        data = request.json
        chat_id = data["chat_id"]
        user_query = data['user_query']
        room = request.headers.get('S-Session-Id')
        info = scraper.extract_info(user_query)
        if(info!= None):
          user_query += "\nInformation : \n" + info
        
        chat = None
        history = []
        is_new_chat = False

        if chat_id == None:
            #new Chat
            is_new_chat = True
            chat = chat_schema.copy()
            chat_id = generate_unique_id()
            chat['chat_id'] = chat_id
            chat['messages'] = []
        else:
            chat_history = collection.find_one({'chat_id': chat_id})
            if(chat_history == None):
                return {"status":"Not Found"}
            
            history = [(message["user_query"],message["bot_response"]) for message in chat_history['messages']]

        message_id = generate_unique_id()
        # Process the user query and generate bot response
        response = glm.emit_bot_response(user_query,history,room,message_id,chat_id,is_new_chat)

        # Insert the response into the database
        final_message = message_schema.copy()
        final_message['message_id'] = message_id
        final_message['user_query'] = user_query
        final_message['bot_response'] = response

        if is_new_chat:
            chat['messages'].append(final_message)
            collection.insert_one(chat)
        else:
            collection.update_one( 
                { 'chat_id': chat_id },
                { '$push': { 'messages': final_message } }
            )
        return {
                "status":"ok",
                'chat_id':chat_id,
                'new_chat':is_new_chat,
                "message_id": message_id,
                "message": [
                    {
                    "author": "user",
                    "update": True,
                    "content": user_query,
                    },
                    {
                    "author": "bot",
                    "update": True,
                    "content": response,
                    }
                ]
        }
    return generate_response()


if __name__ == "__main__":
    socketio.run(app)