# serve.py

from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from google.cloud import vision

# creates a Flask application, named app
app = Flask(__name__)
app._static_folder = './static'
app.config['SECRET_KEY'] = 'briant'

URI = ''
FACES = []

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()], default = "asdfghkjl;")

# a route where we will display a welcome message via an HTML template
@app.route("/", methods=['GET', 'POST'])
def index():
    message = "Hello, World"
    form = ReusableForm(request.form)
    print("errors: ", form.errors)
    if request.method == 'POST':
        url = request.form['name']
        print("url: ", url) 
        if form.validate():
            # Save the comment here.
            URI = url
            detect_faces_uri(URI)
        else:
            flash('Invalid URL')
    return render_template('index.html', message=message, form=form)


@app.route("/result")
def result():
    message = "Hello, World"
    FACES = []
    return render_template('result.html', message=message)


@app.route("/test")
def test():
    message = "Hello, World"
    return render_template('test.html', message=message)


# api requests
def detect_faces_uri(uri):
    """Detects faces in the file located in Google Cloud Storage or the web."""
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = uri

    response = client.face_detection(image=image)
    FACES = response.face_annotations

    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
    print('Faces:')

    for index, face in enumerate(FACES):
        print('Face {}'.format(index))
        print('anger: {}'.format(face.anger_likelihood))
        print('joy: {}'.format(face.joy_likelihood))
        print('surprise: {}'.format(face.surprise_likelihood))
        print('sorrow: {}'.format(face.sorrow_likelihood))

        print(max(('anger', face.anger_likelihood), ('joy', face.joy_likelihood), ('surprise', face.surprise_likelihood), ('sorrow', face.sorrow_likelihood), key=lambda x: x[1]))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in face.bounding_poly.vertices])

        print('face bounds: {}'.format(','.join(vertices)))

# run the application
if __name__ == "__main__":  
    app.run(debug=True)
