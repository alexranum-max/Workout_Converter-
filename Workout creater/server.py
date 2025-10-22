from flask import Flask, render_template, request, send_file
from Whats_on_Zwift_Scraper import Scrape
from time import time
import os

app = Flask(__name__)
app.jinja_env.globals['time'] = time

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_workout', methods=['POST'])
def create_workout():
    # Debug print to see what Flask receives
    print("Form data received:", request.form)

    # Get the URL from the form
    user_url = request.form.get('url_input')
    if not user_url:
        return f"No URL provided. Form received: {request.form}", 400

    try:
        # Scrape returns the full path of the .zwo file with a unique timestamp
        filepath = Scrape(user_url)

        # Check that file exists
        if not os.path.exists(filepath):
            return "File not found.", 500

        # Send the file to the browser as a download
        return send_file(filepath, as_attachment=True)

    except Exception as e:
        return f"Error running scraper: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
