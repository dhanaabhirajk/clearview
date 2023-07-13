from flask import Flask, render_template, request, make_response

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
