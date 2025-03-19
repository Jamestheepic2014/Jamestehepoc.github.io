import face_recognition
import cv2
import numpy as np
from flask import Flask, render_template, request, url_for
from PIL import Image
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROCESSED_FOLDER'] = 'static/processed'

# Ensure the upload and processed directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Load sample pictures and learn how to recognize them
celebrity_image = face_recognition.load_image_file("celebrity.jpg")
celebrity_face_encoding = face_recognition.face_encodings(celebrity_image)[0]

billionaire_image = face_recognition.load_image_file("billionaire.jpg")
billionaire_face_encoding = face_recognition.face_encodings(billionaire_image)[0]

actor_image = face_recognition.load_image_file("actor.jpg")
actor_face_encoding = face_recognition.face_encodings(actor_image)[0]

musician_image = face_recognition.load_image_file("musician.jpg")
musician_face_encoding = face_recognition.face_encodings(musician_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    celebrity_face_encoding,
    billionaire_face_encoding,
    actor_face_encoding,
    musician_face_encoding
]
known_face_names = [
    "Celebrity",
    "Billionaire",
    "Actor",
    "Musician"
]

# Initialize variables to count the number of people from each decade
decade_counts = {
    "1940s": 0,
    "1950s": 0,
    "1960s": 0,
    "1970s": 0,
    "1980s": 0,
    "1990s": 0,
    "2000s": 0,
    "2010s": 0,
    "2020s": 0
}

# Assuming you have a way to determine the decade of the person in the image
# For example, you could have a dictionary that maps names to decades
name_to_decade = {
    "Celebrity": "1980s",
    "Billionaire": "1990s",
    "Actor": "2000s",
    "Musician": "2010s"
}

# Assuming you have a way to determine if a person has a Wikipedia article
# For example, you could have a set of names of people who have Wikipedia articles
wikipedia_people = {"Celebrity", "Billionaire", "Actor", "Musician"}

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return render_template('index.html', message='No file uploaded')
        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return render_template('index.html', message='No file selected')

        if file:
            # Save the uploaded image
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Load the uploaded image
            unknown_image = face_recognition.load_image_file(file_path)

            # Find all the faces and face encodings in the unknown image
            face_locations = face_recognition.face_locations(unknown_image)
            face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

            # Convert the image to BGR color (which OpenCV uses)
            unknown_image_cv2 = cv2.cvtColor(unknown_image, cv2.COLOR_RGB2BGR)

            # Initialize variables to count the number of each type of person
            celebrity_count = 0
            billionaire_count = 0
            actor_count = 0
            musician_count = 0

            # Initialize a variable to count the number of people with Wikipedia articles
            wikipedia_count = 0

            # Reset decade counts
            for decade in decade_counts:
                decade_counts[decade] = 0

            # Loop through each face found in the unknown image
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # If a match was found in known_face_encodings, use the first one
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]

                    # Increment the count for the identified person
                    if name == "Celebrity":
                        celebrity_count += 1
                    elif name == "Billionaire":
                        billionaire_count += 1
                    elif name == "Actor":
                        actor_count += 1
                    elif name == "Musician":
                        musician_count += 1

                    # Increment the count for the identified decade
                    if name in name_to_decade:
                        decade = name_to_decade[name]
                        decade_counts[decade] += 1

                    # Increment the count for people with Wikipedia articles
                    if name in wikipedia_people:
                        wikipedia_count += 1

                # Draw a box around the face
                cv2.rectangle(unknown_image_cv2, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(unknown_image_cv2, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(unknown_image_cv2, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Save the image with the bounding boxes
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], 'output.jpg')
            cv2.imwrite(output_path, unknown_image_cv2)

            return render_template(
                'index.html',
                message='Image processed!',
                celebrity_count=celebrity_count,
                billionaire_count=billionaire_count,
                actor_count=actor_count,
                musician_count=musician_count,
                decade_counts=decade_counts,
                wikipedia_count=wikipedia_count,
                image_path='processed/output.jpg'  # Path to the processed image
            )

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Person Identifier</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
    <div class="container">
        <h1>Person Identifier</h1>
        {% if message %}
            <div class="message">{{ message }}</div>
        {% endif %}
        <form method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="file">Upload Image:</label>
                <input type="file" name="file" id="file" required>
            </div>
            <button type="submit">Upload and Identify</button>
        </form>
        {% if image_path %}
            <h2>Processed Image</h2>
            <img src="{{ url_for('static', filename=image_path) }}" alt="Processed Image">
            <h2>Counts</h2>
            <p>Number of Celebrities: {{ celebrity_count }}</p>
            <p>Number of Billionaires: {{ billionaire_count }}</p>
            <p>Number of Actors: {{ actor_count }}</p>
            <p>Number of Musicians: {{ musician_count }}</p>
            <h2>Decade Counts</h2>
            {% for decade, count in decade_counts.items() %}
                <p>Number of people from the {{ decade }}: {{ count }}</p>
            {% endfor %}
            <h2>Wikipedia Count</h2>
            <p>Number of people with Wikipedia articles: {{ wikipedia_count }}</p>
        {% endif %}
    </div>
</body>
</html>
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background-color: #f0f0f0;
}

.container {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.message {
    color: red;
    margin-bottom: 10px;
}

.success {
    color: green;
}

.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 5px;
}

input[type="file"] {
    display: block;
    margin: 0 auto;
}

button {
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

button:hover {
    background-color: #45a049;
}

img {
    max-width: 100%;
    height: auto;
    margin-top: 20px;
}
