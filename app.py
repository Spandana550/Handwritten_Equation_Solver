import time
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import cv2
import numpy as np
from keras.models import model_from_json # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_from_directory
from werkzeug.utils import secure_filename
import os
import base64
import io
from PIL import Image

app = Flask(__name__)
app.secret_key = '~<\xbb)\xe6>\x88\xd8\xe4q\xb4\x9c\xb8\xe0\xee\x08\xc2\xdd\xdb\x1e!\xfb\xf8z'

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/eqsolver'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model for the database
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Load the trained model
json_file = open("model/model_final.json", 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# Load model weights
loaded_model.load_weights("model/model.weights.h5")

def process_image(img):
    if img is not None:
        img = ~img
        ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        ctrs, ret = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
        w = int(45)
        h = int(45)
        train_data = []
        rects = []
        for c in cnt:
            x, y, w, h = cv2.boundingRect(c)
            rect = [x, y, w, h]
            rects.append(rect)
        bool_rect = []
        for r in rects:
            l = []
            for rec in rects:
                flag = 0
                if rec != r:
                    if r[0] < (rec[0] + rec[2] + 10) and rec[0] < (r[0] + r[2] + 10) and r[1] < (rec[1] + rec[3] + 10) and \
                            rec[1] < (r[1] + r[3] + 10):
                        flag = 1
                    l.append(flag)
                if rec == r:
                    l.append(0)
            bool_rect.append(l)
        dump_rect = []
        for i in range(0, len(cnt)):
            for j in range(0, len(cnt)):
                if bool_rect[i][j] == 1:
                    area1 = rects[i][2] * rects[i][3]
                    area2 = rects[j][2] * rects[j][3]
                    if area1 == min(area1, area2):
                        dump_rect.append(rects[i])
        final_rect = [i for i in rects if i not in dump_rect]
        for r in final_rect:
            x = r[0]
            y = r[1]
            w = r[2]
            h = r[3]
            im_crop = thresh[y:y + h + 10, x:x + w + 10]
            im_resize = cv2.resize(im_crop, (45, 45))
            im_resize = np.reshape(im_resize, (45, 45, 1))
            train_data.append(im_resize)

        s = ''
        for i in range(len(train_data)):
            train_data[i] = np.array(train_data[i])
            train_data[i] = train_data[i].reshape(1, 45, 45, 1)
            result = np.argmax(loaded_model.predict(train_data[i]), axis=-1)
            if result[0] == 10:
                s = s + '+'
            if result[0] == 11:
                s = s + '-'
            if result[0] == 12:
                s = s + '*'
            if result[0] == 0:
                s = s + '0'
            if result[0] == 1:
                s = s + '1'
            if result[0] == 2:
                s = s + '2'
            if result[0] == 3:
                s = s + '3'
            if result[0] == 4:
                s = s + '4'
            if result[0] == 5:
                s = s + '5'
            if result[0] == 6:
                s = s + '6'
            if result[0] == 7:
                s = s + '7'
            if result[0] == 8:
                s = s + '8'
            if result[0] == 9:
                s = s + '9'
            if result[0] == 13:
                s = s + '('
            if result[0] == 14:
                s = s + ')'
            if result[0] == 15:
                s = s + '/'
            if result[0] == 16:
                s = s + '/'

        return s

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))

        new_user = User(firstname=firstname, lastname=lastname, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('predict'))
        else:
            flash('Invalid email or password')

    return render_template('login.html')


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    # Check if the user is logged in
    if 'user_id' not in session:
        print('Please login to access this feature')
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file:
            # Save the file to the upload folder
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Read the saved file and process it
            image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if image is not None:
                equation = process_image(image)
                if equation:
                    # Check for division by zero
                    if '/' in equation:
                        operands = equation.split('/')
                        if len(operands) == 2 and operands[1] == '0':
                            return render_template('index.html', error_message='Cannot divide by zero (undefined)', uploaded_image=filename)
                    
                    # Check for multiplication by zero
                    if '*' in equation:
                        operands = equation.split('*')
                        if '0' in operands:
                            return render_template('index.html', error_message='Multiplication by zero results in zero', uploaded_image=filename)
                    
                    # Evaluate the equation
                    try:
                        result = eval(equation)
                        # Check for syntax errors
                        if isinstance(result, (int, float)):
                            # Pass the filename to the template for display
                            return render_template('index.html', equation=equation, result=result, uploaded_image=filename)
                        else:
                            return render_template('index.html', error_message='Syntax Error in Equation', uploaded_image=filename)
                    except ZeroDivisionError:
                        return render_template('index.html', error_message='Cannot divide by zero (undefined)', uploaded_image=filename)
                    except Exception as e:
                        error_message = f'Syntax Error in Equation: {equation}'
                        return render_template('index.html', error_message=error_message, uploaded_image=filename)
                else:
                    return render_template('index.html', error_message='Error processing the image')
            else:
                return render_template('index.html', error_message='Failed to read the uploaded image')

    return render_template('index.html')




if __name__ == '__main__':
    app.run(debug=True)
