# serve.py

from flask import Flask, render_template, flash, request, redirect
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from google.cloud import vision
from PIL import Image, ImageFilter
import requests
import pathlib
import io
from googleapiclient.discovery import build
import pprint

# creates a Flask application, named app
app = Flask(__name__)
app._static_folder = './static'
app.config['SECRET_KEY'] = 'briant'

class ReusableForm(Form):
    name = TextField('URL:', validators=[validators.required(), 
        validators.url()], default = "Url Here")

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
            objects = localize_objects_uri(url)
            faces = detect_faces_uri(url)
            mask_objects(url, objects)
            mask_faces(url, faces)
            return redirect('result')
        else:
            flash('Invalid URL')
    return render_template('index.html', message=message, form=form)


@app.route("/result")
def result():
    message = "Hello, World"
    return render_template('result.html', message=message)


@app.route("/test1")
def test():
    message = "Hello, World"
    return render_template('test1.html', message=message)


# api requests
def detect_faces_uri(uri):
    """Detects faces in the file located in Google Cloud Storage or the web."""
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = uri

    response = client.face_detection(image=image)
    faces = response.face_annotations

    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
    print('Faces:', len(faces))

    for index, face in enumerate(faces):
        print('Face {}'.format(index))
        print('anger: {}'.format(face.anger_likelihood))
        print('joy: {}'.format(face.joy_likelihood))
        print('surprise: {}'.format(face.surprise_likelihood))
        print('sorrow: {}'.format(face.sorrow_likelihood))
        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in face.bounding_poly.vertices])
        print('face bounds: {}'.format(','.join(vertices)))
    return faces

def localize_objects_uri(uri):
    """Localize objects in the image on Google Cloud Storage

    Args:
    uri: The path to the file in Google Cloud Storage (gs://...)
    """    
    client = vision.ImageAnnotatorClient()

    image = vision.types.Image()
    image.source.image_uri = uri

    objects = client.object_localization(
        image=image).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    for o in objects:
        print(o.name)
    return objects

def mask_objects(url, objects):
    avoid=['Person', 'Woman', 'Man']
    try:
        response = requests.get(url)
    except:
        print('Invalid image URL')
    img = Image.open(io.BytesIO(response.content))
    img.convert('RGB')
    imgwidth, imgheight = img.size
    img.save("./static/rawimg.jpeg", "JPEG")
    for obj in objects:
        if obj.score > 0.5 and obj.name not in avoid:
            print(obj.name, obj.score)
            verticies = ([(int(vertex.x * imgwidth), int(vertex.y * imgheight)) 
                for vertex in obj.bounding_poly.normalized_vertices])
            width = abs(verticies[0][0] - verticies[1][0])
            height = abs(verticies[1][1] - verticies[2][1])
            print("w, h: ", width, height)
            try:
                response = requests.get(search(obj.name))
                emj = Image.open(io.BytesIO(response.content))
                emj.convert('RGBA')
                emj = emj.resize((width, height))
                img.paste(emj, verticies[0], emj)
            except:
                print('Invalid image URL')
    img.save("./static/midimg.jpeg", "JPEG")

def search(term):
    service = build("customsearch", "v1", developerKey="AIzaSyBdWD6hJRx8IKY6ueqHFXc6Dy1xCFwDrHE")
    res = service.cse().list(q=term,cx='018117316144593518101:jr7ol9zygzk',).execute()
    url = res['items'][0]['pagemap']['cse_image'][0]['src']
    return url

def mask_faces(url, faces):
    try:
        response = requests.get(url)
    except:
        print('Invalid image URL')
    img = Image.open(pathlib.Path('./static/midimg.jpeg'))
    img.convert('RGB')
    
    emotions={'anger':'images/angrybear.png', 'joy':'images/happybear.png', 
        'surprise':'images/surprisebear.png', 'sorrow':'images/sadbear.png'}
    for face in faces:                
        emotion = max(('anger', face.anger_likelihood), ('joy', face.joy_likelihood), 
            ('surprise', face.surprise_likelihood), ('sorrow', face.sorrow_likelihood), key=lambda x: x[1])
        print(emotion)
        verticies = ([(vertex.x, vertex.y) for vertex in face.bounding_poly.vertices])
        width = abs(verticies[0][0] - verticies[1][0])
        height = abs(verticies[1][1] - verticies[2][1])
        print("w, h: ", width, height)
        emj = Image.open(emotions[emotion[0]])
        emj = emj.resize((width, height))
        emj.convert('RGBA')
        img.paste(emj, verticies[0], emj)
    img.save("./static/modimg.jpeg", "JPEG")


# run the application
if __name__ == "__main__":  
    app.run(debug=True)
