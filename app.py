from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)
import os
import pyodbc
import json
from azure.storage.blob import BlobServiceClient
import requests

app = Flask(__name__)

current_user = -1
current_username = " "
current_wardrobe = " "

@app.route('/')
def index():
    current_user = -1
    current_username = " "
    print('Request for index page received')
    return render_template('index.html')

@app.route('/FindAThread.ico')
def findAThreadLogo():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'FindAThreadLogo.ico', mimetype='image/vnd.microsoft.icon')

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


def get_nearest_basic_color(hex_code):
    basic_colors = {
        "Red": (255, 0, 0),
        "Green": (0, 128, 0),
        "Blue": (0, 0, 255),
        "Yellow": (255, 255, 0),
        "Orange": (255, 165, 0),
        "Purple": (128, 0, 128),
        "Pink": (255, 192, 203),
        "Brown": (165, 42, 42),
        "Gray": (128, 128, 128),
        "Black": (0, 0, 0),
        "White": (255, 255, 255),
        "Cyan": (0, 255, 255),
        "Magenta": (255, 0, 255),
        "Lime": (0, 255, 0),
        "Teal": (0, 128, 128),
        "Navy": (0, 0, 128),
        "Maroon": (128, 0, 0),
        "Olive": (128, 128, 0),
        "Turquoise": (64, 224, 208),
        "Gold": (255, 215, 0),
        "Silver": (192, 192, 192),
        "Violet": (238, 130, 238),
        "Indigo": (75, 0, 130),
        "Aquamarine": (127, 255, 212),
    }

    hex_code = hex_code.lstrip("#")
    target_rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

    current_near_color = ""
    current_nearest_value = float("inf")

    for color, rgb in basic_colors.items():
        color_diff = abs(rgb[0] - target_rgb[0]) + abs(rgb[1] - target_rgb[1]) + abs(rgb[2] - target_rgb[2])
        if color_diff < current_nearest_value:
            current_near_color = color
            current_nearest_value = color_diff

    return current_near_color     


    
def get_color_name(rgb):

    rgb = tuple(int(value) for value in rgb)

    # Make a request to the Color API
    print("https://www.thecolorapi.com/id?rgb=" + str(rgb[0]) + "," + str(rgb[1]) + "," + str(rgb[2]) + "&format=json")
    response = requests.get(f"https://www.thecolorapi.com/id?rgb=" + str(rgb[0]) + "," + str(rgb[1]) + "," + str(rgb[2]) + "&format=json")

    if response.status_code == 200:
        color_data = response.json()
        color_name = color_data['name']['value']
        color_hex = color_data['hex']['value']
        #print (color_hex)
        print(get_nearest_basic_color(color_hex))
        return color_name
    else:
        return None

def imageProcess(image_url):
    from google.cloud import vision
    print("Image processing started.")

    try:
        # Set the environment variable for service account credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'findathread-c2b11579a81c.json'

        # Authenticate the client
        client = vision.ImageAnnotatorClient()

        # Perform the desired Vision API tasks using the client

        # Example: Perform label detection
        image = vision.Image()
        image.source.image_uri = image_url

        response = client.label_detection(image=image)
        labels = response.label_annotations

        # Print the labels for testing
        print("Labels:")
        for label in labels:
            print(label.description)

        # Example: Extract dominant colors
        response = client.image_properties(image=image)
        dominant_colors = response.image_properties_annotation.dominant_colors.colors

        # Print the dominant colors for testing
        print("Dominant Colors:")
        color = dominant_colors[0].color
        color_rgb = (color.red, color.green, color.blue)
        
        color_name = get_color_name(color_rgb)
        print(color_name)
        
        
        # Return any extracted information or perform further processing
    except Exception as e:
        # Print any errors that occur during authentication or API calls
        print(f"Error occurred during Vision API processing: {str(e)}")
        raise

    print("Image processing completed.")

@app.route('/upload', methods=['POST'])
def upload():
    storage_account_key = "lMD3BaFpJCcz5cN7vMa+/XANoUaUOWVINZCeqOvDIu/fWnXTVGU2ysMuZhwWovJwJ+WDbqaL1fbN+AStr2YFfg=="
    storage_account_name = "findathreadcontainer"

    file = request.files['file']
    gender = request.form['gender']
    print("GENDER SELCETED: " + gender)
    if file:
        connection_string = "DefaultEndpointsProtocol=https;AccountName=findathreadcontainer;AccountKey=lM/MQ4LQ8XVjlZoz8l122v2bNgIwo3k/Yc6v/WXmwdhZpD6aXDbAqX9h3L8v2IPFTFoC07y120fJ+AStqArU7A==;EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        container_name = "imagestorage"
        container_client = blob_service_client.get_container_client(container_name)

        filename = file.filename

        blob_client = container_client.get_blob_client(filename)

        # Check if the image already exists
        if blob_client.exists():
            # Upload the image
            
            image_url = blob_client.url

            # Perform image processing on the uploaded image
            imageProcess(image_url)
            return jsonify({'status': 'duplicate'})  # Return duplicate image response
        else:
            # Upload the image
            blob_client.upload_blob(file)
            image_url = blob_client.url

            # Perform image processing on the uploaded image
            imageProcess(image_url)
            return jsonify({'status': 'success'})

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

    query = "SELECT WardrobeID AS count FROM [dbo].[Wardrobe] WHERE [WardrobeName] = ?"
    cursor.execute(query, wardrobe_name)
    result = cursor.fetchone()[0]

    current_wardrobe =  result
    print (current_wardrobe)
    # # Close the cursor and connection
    cursor.close()
    cnxn.close()

    return render_template('StartScreen.html')

@app.route('/selectWardrobe', methods=['POST'])
def selectWardrobe():
    wardrobe_id = request.form.get('existing-wardrobe')
    print (wardrobe_id)
    if wardrobe_id is not None:
        try:
            # Establish a connection to the database
            connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:findathreadserver.database.windows.net,1433;Database=findathreaddb;Uid=user1;Pwd={Rr12345678};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
            cnxn = pyodbc.connect(connection_string)

            # Create a cursor object to execute SQL queries
            cursor = cnxn.cursor()

            query = "SELECT WardrobeID AS count FROM [dbo].[Wardrobe] WHERE [WardrobeID] = ?"
            cursor.execute(query, wardrobe_id)
            result = cursor.fetchone()

            if result is not None:
                current_wardrobe = result[0]
                print(current_wardrobe)
                # Close the cursor and connection
                cursor.close()
                cnxn.close()
                return render_template('StartScreen.html')
            
            # Handle the case where no records were found
            return 'No wardrobe found with the specified name'
        
        except Exception as e:
            # Handle any errors that occurred during database access
            return f'Error accessing the database: {str(e)}'
    
    # Handle the case where the wardrobe_name is None
    return 'Failed to select wardrobe'

@app.route('/deleteWardrobe', methods=['POST'])
def deleteWardrobe():
    wardrobe_id = request.form.get('delete-wardrobe')
    
    if wardrobe_id is not None:
        try:
            # Establish a connection to the database
            connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:findathreadserver.database.windows.net,1433;Database=findathreaddb;Uid=user1;Pwd={Rr12345678};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
            cnxn = pyodbc.connect(connection_string)

            # Create a cursor object to execute SQL queries
            cursor = cnxn.cursor()

            # Perform the delete operation using the wardrobe_id
            delete_query = "DELETE FROM [dbo].[Wardrobe] WHERE [WardrobeID] = ?"
            cursor.execute(delete_query, wardrobe_id)
            cnxn.commit()

            # Close the cursor and connection
            cursor.close()
            cnxn.close()

            return render_template('index.html')
        
        except Exception as e:
            # Handle any errors that occurred during database access
            return f'Error accessing the database: {str(e)}'
    
    # Handle the case where the wardrobe_id is None
    return 'Failed to delete wardrobe'

@app.route('/tops',methods=['GET', 'POST'])
def tops():
     # Establish a connection to the database
    connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:findathreadserver.database.windows.net,1433;Database=findathreaddb;Uid=user1;Pwd={Rr12345678};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    cnxn = pyodbc.connect(connection_string)

    # Create a cursor object to execute SQL queries
    cursor = cnxn.cursor()

    cursor.execute('SELECT ImageURL FROM Clothing')
    rows = cursor.fetchall()

    # Extract the image URLs from the query results
    imageURLs = [row.ImageURL for row in rows if row.ImageURL]

    # Close the cursor and connection
    cursor.close()
    cnxn.close()

    # Render the HTML template and pass the image URLs to it
    return render_template('Tops.html', imageURLs=imageURLs)
    

if __name__ == '__main__':
    app.run()