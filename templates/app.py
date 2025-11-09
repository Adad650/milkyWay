from flask import Flask, send_from_directory, send_file, redirect, url_for
import os

app = Flask(__name__, static_folder='static')

# Ensure the static directory exists
os.makedirs('static', exist_ok=True)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/play')
def play():
    # In a real app, you might want to add game state initialization here
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Run the app
    app.run(port=17464, debug=True)
