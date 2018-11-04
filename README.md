# refrigerator

Cal Hacks 5.0

Project Name: Bear Faced

Authors: Brian Fu, Bryant Bettencourt

About the Project:

Bear Faced is a web-application that uses Google's Facial Recognition and Image Search Recognition API's to detect objects and faces in pictures. The program identifies objects or faces in a picture, and then returns another picture with clipart of those objects and faces proportionally masked over the origianl picture. Using the Google's Facial Recognition API, we were able to identify different emotions of people's faces. A happy, sad, surprised, or angry face is replaced by a happy, sad, surprised, or angry bear. 

How to Build:

- pip install requirments.txt 
- python serve.py
- localhost:5000

WorkFlow

Images are passed in as URLs to Google CLoud Vision API where they are annotated for human facial features and locally labeled objects. The returned JSON object is parsed for a feature vector containing the locations of each landmark. If the landmark is a face, the appropriate bear is overlayed at the angle of the head. If the landmark is an object, a Google Custom Query is run on the Emojipedia domain and the emoji image is scraped off of the site. The emoji is then scaled to fit the landmark and pasted onto the original picture. 
