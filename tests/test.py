from flask import Flask, render_template, Response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    def event_stream():
        # Generate some events
        sent_event = False  # Flag to check if the event has been sent

        if not sent_event:
            yield 'data: Event 1\n\n'
            sent_event = True

    return Response(event_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
