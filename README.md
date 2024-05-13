Handwritten Math Equation Solver
AIM of the Project
As the name of the project suggests, we intend to make such a system(Web Interface) in which user will just upload his/her handwritten equation(s) and in return would get the solution to that.

Note: The project is restricted only for Basic Math operations

Implementation
For detecting handwritten equation, we need to detect number and mathematical symbols. So firstly, we trained a CNN(Convolutional Nueral Network) Model over a specified dataset.
Now once the CNN Model was tested enough for detecting handwritten contents, we further proceed to apply some Algebra to solve these detected Equations.
Then, we created a Frontend where user can upload(This project only works when scribbled in a paint application and uploaded in that website) & crop the images of the handwritten equation and can feed it further to the Backend Servers.
The user uploaded images are way to diffrent from the images that CNN demands,Hence we applied Image processing(OpenCV) on the user uploaded image to convert it into a desired image.
Frameworks & Modules Used
Tensorflow & Keras (for Training & Testing CNN Model)
Flask Web Framework (for Backend)
HTML,CSS,JS(for Frontend)
OpenCV Library of Python (for Image Processing)
sympy module(Handles all equation Solving)

Working of the Project:
1. The user can scribble some basic math operation like 2+3 or combinations like 2+5-6 in the paint application. Take a screenshot and save it.
2. After registering and loggingi in to the website. Upload that screenshot and click upload.
3. The uploaded image and the recognized equation and its solution is displayed below the upload button.

![image](https://github.com/Spandana550/Handwritten_Equation_Solver/assets/134623596/89b0adcb-ee1c-49e6-a168-04986ec4d564)
![image](https://github.com/Spandana550/Handwritten_Equation_Solver/assets/134623596/0509030d-02d5-4291-a03f-585e50a8eb92)

How to run:
1.Download the zip file
2.Setup Xampp server. Turn on Apache and Mysql
3.In phpmyadmin create the database by importing the eqsolver.sql
4.In the terminal , run "python app.py"
5.Visit localhost:5000 to see the webpage
