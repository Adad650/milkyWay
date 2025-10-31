from flask import Flask, send_from_directory, render_template, redirect, url_for
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

# Ensure the static directory exists
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/play')
def play():
    # In a real app, you might want to add game state initialization here
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create a symbolic link to index.html in the templates directory if it doesn't exist
    if not os.path.exists('templates/index.html'):
        try:
            os.symlink('../index.html', 'templates/index.html')
        except FileExistsError:
            pass
    
    # Run the app
    app.run(port=17464, debug=True)
