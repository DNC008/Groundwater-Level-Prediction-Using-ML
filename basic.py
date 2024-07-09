
# from flask import Flask, render_template, request, redirect, url_for
# from datetime import datetime
# import pandas as pd
# import numpy as np
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.preprocessing import StandardScaler
# import pickle

# app = Flask(__name__)

# # Load the trained model
# with open('models/random_forest_model.pkl', 'rb') as file:
#     model = pickle.load(file)

# @app.route('/')
# @app.route('/login.html')
# def login():
#     # Implement login functionality here
#     # For example:
#     # Check if user is logged in, if not, render the login page
#     return render_template('login.html')

# @app.route('/signup.html')
# def signup():
#     return render_template('signup.html')

# @app.route('/sigup_handler.php')
# def signup_handler():
#     return render_template('signup_handler.php')

# @app.route('/login_handler.php')
# def login_handler():
#     return render_template('login_handler.php')

# @app.route('/home.html')
# def home():
#     return render_template('home.html')

# @app.route('/dashboard.html')
# def dashboard():
#     return render_template('dashboard.html')



# @app.route('/predictor')
# def predictor():
#     return render_template('predictor2.html')

# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     prediction = None
#     if request.method == 'POST':
#         # Get input data from the form
#         date_str = request.form['date']
#         water_temperature = float(request.form['water_temperature'])
#         relative_humidity = float(request.form['relative_humidity'])
#         rainfall = float(request.form['rainfall'])
        
#         # Convert date string to datetime object
#         date = datetime.strptime(date_str, '%d-%m-%Y %H:%M')
#         day_of_year = date.timetuple().tm_yday
        
#         # Create input data array
#         input_data = np.array([[water_temperature, relative_humidity, rainfall, day_of_year]])
        
#         # Make prediction
#         prediction = model.predict(input_data)[0]
        
#     return render_template('predictor2.html', prediction=prediction)

# if __name__ == '__main__':
#     app.run(debug=True)




from flask import Flask, render_template, request, redirect, url_for,session, make_response,jsonify
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import sqlite3
from chat import get_response

app = Flask(__name__)

# Set the secret key to enable session usage
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Load the trained model
with open('models/random_forest_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Function to create a connection to the SQLite database
def create_connection():
    conn = sqlite3.connect('database.db')
    return conn

# Create users table if it doesn't exist
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fullname TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

create_table()

@app.route('/')
@app.route('/login.html')
def login():
    # Check if user is already logged in
    if 'email' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup.html')
def signup():
    return render_template('signup.html')

@app.route('/signup_handler.php', methods=['POST'])
def signup_handler():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        
        # Check if the email is already registered
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return "Email already exists. Please try with a different email."
        else:
            cursor.execute("INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)", (fullname, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))

@app.route('/login_handler.php', methods=['POST'])
def login_handler():
    # Handle login form submission
    email = request.form['email']
    password = request.form['password']
    
    # Check if the user exists and the password is correct (using database query)
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['email'] = email
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))



@app.route('/logout.html')
def logout():
    # Clear the session to log out the user
    session.clear()
    # Prevent caching of the home page
    response = make_response(redirect(url_for('login')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/logout-confirm.html')
def logout_confirm():
    # Pass the logged_in variable to the template
    return render_template('logout_confirm.html', logged_in=session.get('email') is not None)


@app.route('/home.html')
def home():
  # Check if user is logged in
    if 'email' not in session:
        return redirect(url_for('login'))
    
    # Render the home page
    response = make_response(render_template('home.html'))
    
    # Prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/predictor2.html')
def predictor():
    return render_template('predictor2.html')

@app.route('/weather.html')
def weather():
    return render_template('weather.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

# # Mock model for demonstration purposes
# class MockModel:
#     def predict(self, input_data):
#         # Placeholder prediction logic
#         return np.sum(input_data, axis=1)

# model = MockModel()

# # Mock function for chatbot response
# def get_response(text):
#     # Placeholder chatbot response logic
#     return "Chatbot response to: " + text

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        if request.is_json:
            # Chatbot request
            text = request.json.get('message')
            if text:
                response = get_response(text)
                return jsonify({"answer": response})
            else:
                return jsonify({"error": "No text provided"}), 400
        else:
            # Predictor request
            date_str = request.form.get('date')
            water_temperature = float(request.form.get('water_temperature'))
            relative_humidity = float(request.form.get('relative_humidity'))
            rainfall = float(request.form.get('rainfall'))
            date = datetime.strptime(date_str, '%d-%m-%Y %H:%M')
            day_of_year = date.timetuple().tm_yday
            input_data = np.array([[water_temperature, relative_humidity, rainfall, day_of_year]])
            prediction = model.predict(input_data)[0]

            if prediction < -31.9:
                message = "Groundwater level is low. Consider implementing water-saving measures."
                advice = (
                    "Tips to sustain groundwater:\n"
                    "1. Reduce water usage.\n"
                    "2. Fix leaks.\n"
                    "3. Use rainwater harvesting."
                )
                result_class = "low"
            elif -31.9 <= prediction < -30.6:
                message = "Groundwater level is normal. Continue with regular monitoring."
                advice = (
                    "Tips to sustain groundwater:\n"
                    "1. Practice efficient irrigation.\n"
                    "2. Monitor groundwater usage.\n"
                    "3. Maintain local vegetation."
                )
                result_class = "normal"
            else:
                message = "Groundwater level is high. Be cautious of potential flooding."
                advice = (
                    "Tips to sustain groundwater:\n"
                    "1. Ensure proper drainage.\n"
                    "2. Avoid over-extraction of groundwater.\n"
                    "3. Use permeable materials in construction."
                )
                result_class = "high"
            
            return render_template('predictor2.html', prediction=prediction, message=message, advice=advice, result_class=result_class)
    else:
        return jsonify({"error": "Method not allowed"}), 405 
# @app.route('/predict', methods=['POST'])
# def predict():
#     if request.method == 'POST':
#         if 'message' in request.json:  # Chatbot request
#             text = request.json['message']
#             if text:
#                 response = get_response(text)
#                 return jsonify({"answer": response})
#             else:
#                 return jsonify({"error": "No text provided"}), 400
#         elif 'date' in request.form:  # Predictor request
#             date_str = request.form['date']
#             water_temperature = float(request.form['water_temperature'])
#             relative_humidity = float(request.form['relative_humidity'])
#             rainfall = float(request.form['rainfall'])
#             date = datetime.strptime(date_str, '%d-%m-%Y %H:%M')
#             day_of_year = date.timetuple().tm_yday
#             input_data = np.array([[water_temperature, relative_humidity, rainfall, day_of_year]])
#             prediction = model.predict(input_data)[0]
#             return render_template('predictor2.html', prediction=prediction)
#         else:
#             return jsonify({"error": "Invalid request"}), 400
#     else:
#         return jsonify({"error": "Method not allowed"}), 405
# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     if request.method == 'POST':
#         text=request.get_json().get("message")  # Get input text from the chatbot or predictor form
#         if text:  # Check if text is provided
#             # Check if it's a chatbot request or predictor request
#             if 'date' in request.form:  # Predictor request
#                 # Process predictor form data
#                 date_str = request.form['date']
#                 water_temperature = float(request.form['water_temperature'])
#                 relative_humidity = float(request.form['relative_humidity'])
#                 rainfall = float(request.form['rainfall'])
#                 date = datetime.strptime(date_str, '%d-%m-%Y %H:%M')
#                 day_of_year = date.timetuple().tm_yday
#                 input_data = np.array([[water_temperature, relative_humidity, rainfall, day_of_year]])
#                 prediction = model.predict(input_data)[0]
#                 return render_template('predictor2.html', prediction=prediction)
#             else:  # Chatbot request
#                 response = get_response(text)
#                 return jsonify({"answer": response})
#         else:
#             return jsonify({"error": "No text provided"}), 400
#     else:
#         return jsonify({"error": "Method not allowed"}), 405


# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     prediction = None
#     if request.method == 'POST':
#         # Get input data from the form
#         date_str = request.form['date']
#         water_temperature = float(request.form['water_temperature'])
#         relative_humidity = float(request.form['relative_humidity'])
#         rainfall = float(request.form['rainfall'])
        
#         # Convert date string to datetime object
#         date = datetime.strptime(date_str, '%d-%m-%Y %H:%M')
#         day_of_year = date.timetuple().tm_yday
        
#         # Create input data array
#         input_data = np.array([[water_temperature, relative_humidity, rainfall, day_of_year]])
        
#         # Make prediction
#         prediction = model.predict(input_data)[0]
        
#     return render_template('predictor2.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)



