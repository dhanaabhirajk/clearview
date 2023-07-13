from flask import Flask, render_template, jsonify, request, stream_with_context, Response,make_response
from src import db
from flask_socketio import SocketIO, emit
import uuid
import time
from bson import encode

app = Flask(__name__)
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


@app.route("/")
def homepage():
    response = make_response(render_template("index.html"))
    response.set_cookie("chat_id", value="None")
    return response
    

@app.route("/c/<chat_id>")
def chat_page(chat_id):
    response = make_response(render_template("index.html"))
    response.set_cookie("chat_id", value=chat_id)
    return response

@app.route('/fetch-chat', methods=['GET'])
def fetch_chat():
    chat_id = request.cookies.get("chat_id")
    chat_history = list(collection.find({'chat_id': chat_id}))
    del chat_history[0]['_id']

    # Return the JSON data as bytes
    return chat_history[0]

@app.route('/send-message', methods=['POST'])
def send_message():
    def generate_responses():
        data = request.json
        chat_id = request.cookies.get("chat_id")
        user_query = data['user_query']

        chat_history = collection.find_one({'chat_id': chat_id})
        is_new_chat = chat_history == None
        chat = None
        history = []
        if is_new_chat:
            chat = chat_schema.copy()
            chat_id = generate_unique_id()
            chat['chat_id'] = chat_id
            chat['messages'] = []
        else:
            history = [(message["user_query"],message["bot_response"]) for message in chat_history['messages']]

        message_id = generate_unique_id()
        for response, history in [("How",[("hi","How")]),("How can",[("hi","How can ")]),("How can I ",[("hi","How can I")])]:
        # Process the user query and generate bot response
        # for response, history in model.stream_chat(tokenizer, user_query, history, max_length=max_length,
        #                                            top_p=top_p, temperature=temperature):
            res = {
                'chat_id':chat_id,
                "message_id": message_id,
                "moderations": [
                    {
                    "author": "bot",
                    "update": True,
                    "content": response,
                    }
                ]
                }
            
            socketio.emit('message',res)
            time.sleep(0.00001)


        # Insert the final response into the database
        final_response = response

        final_message = message_schema.copy()
        final_message['message_id'] = message_id
        final_message['user_query'] = user_query
        final_message['bot_response'] = final_response

        if is_new_chat:
            chat['messages'].append(final_message)
            collection.insert_one(chat)
        else:
            collection.update_one( 
                { 'chat_id': chat_id },
                { '$push': { 'messages': final_message } }
            )
        return "success"
    return generate_responses()

if __name__ == '__main__':
    app.run(debug=True)

