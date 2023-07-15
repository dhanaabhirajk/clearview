from src import db,ngrok,scraper,chatGLM
from flask import Flask, render_template, request,make_response
import uuid


app = Flask(__name__)

db_conn = db.connect_to_mongodb()

# Update base URLs to use the public ngrok URL
# app.config["BASE_URL"] = ngrok.open_tunnel()


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
    def generate_response():
        data = request.json
        chat_id = request.cookies.get("chat_id")
        user_query = data['user_query']
        info = scraper.extract_info(user_query)
        if(info!= None):
          user_query += "\nInformation : \n" + info
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
        # Process the user query and generate bot response
        response = chatGLM.get_bot_response(user_query,history)

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

#Production Deployment

if __name__ == '__main__':
    app.run()

#Local Deployment

# if __name__ == '__main__':
#     app.run(debug=True)