# serve.py

from flask import Flask  
from flask import render_template

# creates a Flask application, named app
app = Flask(__name__)
app._static_folder = './static'

# a route where we will display a welcome message via an HTML template
@app.route("/")
def hello():  
    message = "Hello, World"
    return render_template('index.html', message=message)


@app.route("/2")
def hell02():  
    message = "Hello, World"
    return render_template('index2.html', message=message)
    
# run the application
if __name__ == "__main__":  
    app.run(debug=True)
