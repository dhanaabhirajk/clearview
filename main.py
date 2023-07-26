import os
import threading
from src import db, ngrok, scraper, chatGLM
from flask import Flask, render_template, request, make_response, send_from_directory
import uuid
from flask_socketio import SocketIO, emit
from secrets_manager import SECRET_KEY
from src import config

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# Check if the application is running in production mode
p_flag = config.STATUS_ENV == "PRODUCTION"

# Update base URLs to use the public ngrok URL in production
if p_flag:
    app.config["BASE_URL"] = ngrok.open_tunnel()
    app.debug = False
else:
    app.debug = True

# Dictionary to store subprocess functions and their threads for each session (sid)
subprocess_threads = {}

# Create an instance of ProductionChatGLM with p_flag=True
glm = chatGLM.chatGLM(p_flag=p_flag, subprocess_threads=subprocess_threads)
socketio = SocketIO(app)
db_conn = db.connect_to_mongodb()

# MongoDB collection and schemas for chat and message data
collection = db_conn['chats']

chat_schema = {
    'chat_id': '',
    'messages': [],
}
message_schema = {
    'message_id': '',
    'user_query': '',
    'bot_response': '',
}

# Helper function to generate a unique ID
def generate_unique_id():
    return str(uuid.uuid4())

# Helper function to stop generating the bot's response for a session
def stop_generating_response(sid, is_disconnect):
    if sid in subprocess_threads and subprocess_threads[sid]['thread']:
        # Call a custom stop method in the subprocess function (assuming it's designed to stop gracefully)
        subprocess_threads[sid]['stop_flag'] = True
        subprocess_threads[sid]['thread'].join()
        subprocess_threads[sid]['thread'] = None
        subprocess_threads[sid]['response'] = None
        if is_disconnect:
            del subprocess_threads[sid]
    return "ok"

# Function to generate the bot's response to a user query
def generate_response(chat_id, user_query, sid):
    info = scraper.extract_info(user_query)
    if info is not None:
        # Add extracted information to the user query
        user_query += "<br><b>Information :</b> <br>" + info
    
    chat = None
    history = []
    is_new_chat = False

    if chat_id is None:
        # Create a new chat session
        is_new_chat = True
        chat = chat_schema.copy()
        chat_id = generate_unique_id()
        chat['chat_id'] = chat_id
        chat['messages'] = []
    else:
        # Retrieve chat history from the database
        chat_history = collection.find_one({'chat_id': chat_id})
        if chat_history is None:
            return {"status": "Not Found"}
        
        # Extract message history from the chat history
        history = [(message["user_query"], message["bot_response"]) for message in chat_history['messages']]

    # Generate a unique ID for the message
    message_id = generate_unique_id()

    # Process the user query and generate bot response using the chatGLM module
    glm.emit_bot_response(user_query, history, sid, message_id, chat_id, is_new_chat)
    subprocess_threads[sid]['thread'] = None

    # Create the final message to be stored in the database
    final_message = message_schema.copy()
    final_message['message_id'] = message_id
    final_message['user_query'] = user_query
    final_message['bot_response'] = subprocess_threads[sid]['response']['chat']['message'][1]['content']

    if is_new_chat:
        # For a new chat session, add the message to the chat and insert the chat into the database
        chat['messages'].append(final_message)
        collection.insert_one(chat)
    else:
        # For an existing chat session, add the message to the chat history and update the database
        collection.update_one( 
            {'chat_id': chat_id},
            {'$push': {'messages': final_message}}
        )

# Event handler for client connection
@socketio.on("connect")
def on_connect():
    # Generate a unique room name based on the client's session ID
    sid = request.sid
    subprocess_threads[sid] = {'thread': None, 'response': None, 'stop_flag': False}
    emit("connected", {"sid": sid}, room=sid)

# Event handler for client disconnection
@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    # Stop the response generation for the disconnected session
    stop_generating_response(sid, True)

# Flask route for the homepage
@app.route("/")
def homepage():
    response = make_response(render_template("index.html"))
    return response
    
# Flask route for favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Flask route for individual chat page
@app.route("/c/<chat_id>")
def chat_page(chat_id):
    response = make_response(render_template("index.html"))
    return response

# Flask route for fetching chat history
@app.route('/fetch-chat', methods=['POST'])
def fetch_chat():
    data = request.json
    chat_id = data["chat_id"]
    chat_history = list(collection.find({'chat_id': chat_id}))
    if len(chat_history) != 0:
        del chat_history[0]['_id']

        # Return the JSON data as bytes
        return {"status": "ok", "chat": chat_history[0]}
    else:
        return {"status": "Not Found"}

# Flask route for sending user query and getting bot response
@app.route('/send-message', methods=['POST'])
def send_message():
    sid = request.headers.get('S-Session-Id')
    if not subprocess_threads[sid]['thread']:
        data = request.json
        chat_id = data["chat_id"]
        user_query = data['user_query']
        # Create a thread for the subprocess function and start it
        thread = threading.Thread(target=generate_response(chat_id, user_query, sid))
        thread.start()
        thread.join()
    return subprocess_threads[sid]['response']

# Flask route to stop generating bot response for a session
@app.route("/stop-process/", methods=['POST'])
def stop_process():
    sid = request.headers.get('S-Session-Id')
    status = stop_generating_response(sid, False)
    return {"status": status}

# Start the SocketIO server when running the script directly
if __name__ == "__main__":
    socketio.run(app, port=config.PORT)
