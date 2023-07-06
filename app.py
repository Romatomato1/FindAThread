from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
import os
import pyodbc


app = Flask(__name__)

current_user = -1

@app.route('/')
def index():
    current_user = -1
    print('Request for index page received')
    return render_template('index.html')

@app.route('/FindAThread.ico')
def findAThreadLogo():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'FindAThread.ico', mimetype='image/FindAThreadLogo.jpg')

@app.route('/signuppage', methods=['POST'])
def signuppage():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
   # Retrieve the form data
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    email = request.form['email']
    phone = request.form['phone']
    username = request.form['username']
    password = request.form['password']

    # Establish a connection to the database
    connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:findathreadserver.database.windows.net,1433;Database=findathreaddb;Uid=user1;Pwd={Rr12345678};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    cnxn = pyodbc.connect(connection_string)

    # Create a cursor object to execute SQL queries
    cursor = cnxn.cursor()

    # Get the maximum UserID and WardrobeID from the USER table
    cursor.execute("SELECT MAX(UserID) FROM [dbo].[USER]")
    max_user_id = cursor.fetchone()[0]
    max_user_id = 1 if max_user_id is None else max_user_id + 1

    cursor.execute("SELECT MAX(WardrobeID) FROM [dbo].[USER]")
    max_wardrobe_id = cursor.fetchone()[0]
    max_wardrobe_id = 1 if max_wardrobe_id is None else max_wardrobe_id + 1

    # Insert the data into the USER table
    insert_query = "INSERT INTO [dbo].[USER] (WardrobeID, Password, Email, PhoneNumber, ProfilePictrureURL, Username) VALUES (?, ?, ?, ?, ?, ?)"
    cursor.execute(insert_query, (None, password, email, phone, None, username))
    cnxn.commit()

    # Close the cursor and connection
    cursor.close()
    cnxn.close()
    return render_template('index.html')

@app.route('/loginauth', methods=['POST'])
def loginauth():
    username = request.form.get('username')
    password = request.form.get('password')
    print(f"Username: {username}, Password: {password}")


    # Establish a connection to the database
    connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:findathreadserver.database.windows.net,1433;Database=findathreaddb;Uid=user1;Pwd={Rr12345678};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    cnxn = pyodbc.connect(connection_string)
    cursor = cnxn.cursor()

    # Execute the validation query
    query = "SELECT COUNT(*) AS count FROM [dbo].[USER] WHERE [Username] = ? AND [Password] = ?"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()

    count = result.count

    # Check if user exists
    if count > 0:
        print("User authenticated")
        query = "SELECT UserID AS count FROM [dbo].[USER] WHERE [Username] = ? AND [Password] = ?"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()[0]
        current_user = result
        print (current_user)
        return render_template('StartScreen.html')
    else:
        error_message = 'Invalid username or password'
        print(error_message)
        return render_template('index.html', error=error_message)

    
@app.route('/skip', methods=['POST'])
def skip():
    return render_template('StartScreen.html')

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_file = request.files['image']    
    return 'File uploaded sucessfully'

@app.route('/createWardrobe', methods=['POST'])
def createWardrobe():
    return render_template('AddToWardrobe.html')

if __name__ == '__main__':
    app.run()
