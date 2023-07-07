from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
import os
import pyodbc
import json


app = Flask(__name__)

current_user = -1
current_username = " "

@app.route('/')
def index():
    current_user = -1
    current_username = " "
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

def get_existing_wardrobes():
    # Establish a connection to the database
    connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:findathreadserver.database.windows.net,1433;Database=findathreaddb;Uid=user1;Pwd={Rr12345678};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    conn = pyodbc.connect(connection_string)

    # Execute the query to retrieve existing wardrobe names
    cursor = conn.cursor()
    cursor.execute("SELECT WardrobeID, WardrobeName FROM WARDROBE")
    rows = cursor.fetchall()

    # Create a list of dictionaries with wardrobe IDs and names
    existing_wardrobes = [{'id': row[0], 'name': row[1]} for row in rows]

    # Close the cursor and connection
    cursor.close()
    conn.close()
    print (existing_wardrobes)
    return existing_wardrobes

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
        current_username = username
        print (current_user)
        print (current_username)
        # Existing wardrobe data from the database
        existing_wardrobes = get_existing_wardrobes()  # Replace with your implementation
        return render_template('AddToWardrobe.html', existing_wardrobes=existing_wardrobes)
    else:
        error_message = 'Invalid username or password'
        print(error_message)
        return render_template('index.html', error=error_message)

    
@app.route('/skip', methods=['POST'])
def skip():
    return render_template('StartScreen.html')

@app.route('/createOutfit', methods=['POST'])
def createOutfit():
    return render_template('CreateAnOutfit.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        filename = file.filename
        file.save('uploads/' + filename)
        # Add your code to handle the uploaded file as needed
        return render_template('AddToWardrobe.html')
    else:
        return 'No file selected'

@app.route('/newWardrobe', methods=['POST'])
def newWardrobe():
    wardrobe_name = request.form.get('wardrobe-name')
     # Establish a connection to the database
    connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:findathreadserver.database.windows.net,1433;Database=findathreaddb;Uid=user1;Pwd={Rr12345678};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    cnxn = pyodbc.connect(connection_string)

    # # Create a cursor object to execute SQL queries
    cursor = cnxn.cursor()

    insert_query = "INSERT INTO [dbo].[Wardrobe] (ClothingID,wardrobeName,Stock) VALUES (?,?,?)"
    cursor.execute(insert_query, (None,wardrobe_name,None))
    cnxn.commit()

    # # Close the cursor and connection
    cursor.close()
    cnxn.close()

    return render_template('StartScreen.html')

    

if __name__ == '__main__':
    app.run()