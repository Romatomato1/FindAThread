from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify, flash)
import os
import pyodbc
import json
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import requests
import nltk
from rembg import remove
from PIL import Image
from io import BytesIO
nltk.download('punkt')
from Outfit import Outfit
from User import User
app = Flask(__name__)
app.secret_key = 'FindAThreadSecretKey'
user = User()
outfit = Outfit()

@app.route('/')
def index():
    print('Request for index page received')
    return render_template('index.html', user=user)

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
connection_string
    cnxn = pyodbc.connect(connection_string)

    # Create a cursor object to execute SQL queries
    cursor = cnxn.cursor()

    # Insert the data into the USER table
    insert_query = "INSERT INTO [dbo].[USER] (Password, Email, PhoneNumber, ProfilePictrureURL, Username) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(insert_query, (password, email, phone, None, username))
    cnxn.commit()

    # Close the cursor and connection
    cursor.close()
    cnxn.close()
    return render_template('index.html')

def get_existing_wardrobes():
    # Establish a connection to the database
connection_string
    conn = pyodbc.connect(connection_string)

    # Execute the query to retrieve existing wardrobe IDs and names
    cursor = conn.cursor()
    cursor.execute("SELECT W.WardrobeID, W.WardrobeName FROM UserWardrobe UW JOIN WARDROBE W ON UW.WardrobeID = W.WardrobeID WHERE UW.UserID = ?", user.current_user)
    rows = cursor.fetchall()

    # Create a list of dictionaries with wardrobe IDs and names
    existing_wardrobes = [{'id': row[0], 'name': row[1]} for row in rows]

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print(existing_wardrobes)
    return existing_wardrobes

@app.route('/loginauth', methods=['POST'])
def loginauth():
    username = request.form.get('username')
    password = request.form.get('password')
    print(f"Username: {username}, Password: {password}")


    # Establish a connection to the database
connection_string
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
        user.current_user = cursor.fetchone()[0]
        print (user.current_user)
        # Existing wardrobe data from the database
        existing_wardrobes = get_existing_wardrobes()  # Replace with your implementation
        return render_template('AddToWardrobe.html', existing_wardrobes=existing_wardrobes,user=user)
    else:
        error_message = 'Invalid username or password'
        print(error_message)
        return render_template('index.html', error=error_message)

@app.route('/logout', methods=['POST'])
def logout():
    user.current_user = -1
    user.current_wardrobe=""
    return render_template('index.html',user=user)

@app.route('/skip', methods=['POST'])
def skip():
    existing_outfits = get_existing_outfits()
    return render_template('StartScreen.html', existing_outfits = existing_outfits)

@app.route('/createOutfit', methods=['POST'])
def createOutfit():
    outfit = Outfit()
    return render_template('CreateAnOutfit.html', outfit=outfit, user=user)


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
        return get_nearest_basic_color(color_hex)
    else:
        return None

def imageToDatabase(detected_words, labels, image_url, color_name, gender):
    
    from nltk.tokenize import word_tokenize
    
    #Categories for the clothing items
    
    head_objects = ["hat", "cap", "beanie", "visor", "headband", "sun hat", "fedora"]
    top_objects = ["outerwear", "top", "shirt", "coat", "brassiere", "dress", "longcoat"]
    bottom_objects = ["shorts", "pants", " jeans", "trousers", "skirt"]
    shoes_objects = ["sneakers", "shoe", "boot", "sandals", "slippers"]
    
    
    head_labels = ["headwear", "hat", "cap", "beanie", "visor", "baseball cap", "sun hat", "fedora", "bucket hat", "beret",
                    "headband", "turban", "bandana", "cricket cap", "helmet"]
    
    top_labels = ["sleeve", "collar" , "t-shirt", "button", "pocket", "coat", "dress shirt", "neck", "blazer", "jacket", "formal Wear", "sweatshirt", "jersey", 
                    "long-sleeved t-shirt", "hoodie", "overcoat", "active shirt", "one-piece garment", "sleeveless shirt", "day dress", "trench coat", 
                    "lingerie top", "brassiere", "lingerie", "cocktail dress", "vest", "active tank", "tank", "tank top", "workwear", "duster", "gown", 
                    "chest", "shoulder"]
    
    bottom_labels = ["shorts", "active shorts", "active pants", "trunk", "waist", "jeans" , "torusers", "thigh", "knee", "pocket", "board short", 
                        "yoga pants", "leggins", "sweatpants", "tights", "cargo pants", "one-piece garment", "day dress"]
    
    shoes_labels = ["sneakers", "running shoes", "athletic shoes", "sports shoes", "tennis shoes", "trainers", "boots", "ankle boots", "knee-high boots", "combat boots",
                    "work boots", "hiking boots", "pumps", "high heels", "stiletto heels", "wedges", "platform heels", "sandals", "flip flops", "slippers",
                    "loafers", "ballet flats", "oxford shoes", "moccasins", "espadrilles", "slingback shoes", "mary jane shoes", "suede shoes", "leather shoes", "canvas shoes"]

    
    top_descriptive_labels = {"shirt" : "shirt", "sleeve" : "with sleeve", "collar" : "collared", "t-shirt" : "t-shirt ", "button" : "buttoned", "pocket" : "with pockets", 
                            "coat" : "coat", "dress shirt" : "dress shirt", "blazer" : "blazer", "jacket" : "jacket", "sweatshirt" : "sweatshirt", "jersey" : "jersey", 
                            "long-sleeved t-shirt" : "long sleeved shirt", "hoodie" : "hoodie", "overcoat" : "overcoat", "active shirt" : "active shirt", 
                            "one-piece garment" : "one piece", "sleeveless shirt" : "sleeveless shirt", "day dress" : "dress", "trench coat" : "long coat", 
                            "lingerie top" : "top", "brassiere" : "brassiere", "lingerie" : "lingerie", "cocktail dress" : "dress", "vest" : "vest", 
                            "active tank" : "tank", "tank" : "tank", "tank top" : "tank top", "duster" : "loose fitting" , "gown" : "gown"}
    
    bottom_descriptive_labels = {"shorts" : "shorts", "active shorts" : "active shorts", "active pants" : "pants", "trunk" : "trunks", "jeans" : "jeans",
                                 "trousers" : " trousers", "pocket" : "with pockets", "board short" : "board shorts", "yoga pants" : "yoga pants", "leggins" : "leggins", 
                                 "sweatpants" : "sweatpants", "tights" : "tights", "cargo pants" : "cargo pants", "one-piece garment" : "one piece"}
    
    shoe_descriptive_labels = {"sandal" : "sandals", "high heels" : "high heels", "dress shoe" : "dress shoe", "slipper" : "slippers", "sneakers" : "sneakers", "sportswear" : "sportswear"}
    
    def calculate_category(given_labels, potential_labels):
        given_tokens = set(word_tokenize(' '.join(given_labels)))
        potential_tokens = set(word_tokenize(' '.join(potential_labels)))
        intersection_count = len(given_tokens.intersection(potential_tokens))
        union_count = len(given_tokens.union(potential_tokens))
        return intersection_count / union_count

    def get_description(given_labels, descriptive_labels):
        matched_labels = []
        for label in given_labels:
            if label in descriptive_labels:
                matched_labels.append(descriptive_labels[label])
            
        return ', '.join(matched_labels).capitalize()
        
        
    given_objects = [word.lower() for word in detected_words]
    given_labels = [label.description.lower() for label in labels]

    # Check for exact word-to-word matches
    if any(obj in given_objects for obj in head_objects):
        head_score = 1.0
    else:
        head_score = calculate_category(given_labels, head_labels)

    if any(obj in given_objects for obj in top_objects):
        top_score = 1.0
    else:
        top_score = calculate_category(given_labels, top_labels)

    if any(obj in given_objects for obj in bottom_objects):
        bottom_score = 1.0
    else:
        bottom_score = calculate_category(given_labels, bottom_labels)

    if any(obj in given_objects for obj in shoes_objects):
        shoe_score = 1.0
    else:
        shoe_score = calculate_category(given_labels, shoes_labels)

    scores = {
        "Head": head_score,
        "Top": top_score,
        "Bottom": bottom_score,
        "Shoe": shoe_score
    }

    best_match = max(scores, key=scores.get)
    print(f"Best Match: {best_match}")
        
    if(best_match == 'Head'):
        category = 2
        
        if(scores["Head"] == 1.0): #get the name of the object for the descriptiom
            obj_name_set = set(given_objects).intersection(head_objects)
            obj_name = ", ".join(obj_name_set)
        else:
            obj_name = "headwear"
        
        description = f"{color_name} {gender}'s {obj_name}"
        print(f"Image Description: {description}")
        
    elif(best_match == 'Top'):
        category = 0 #get the category for categoryID
        
        if(scores["Top"] == 1.0): #get the name of the object for the descriptiom
            obj_name_set = set(given_objects).intersection(top_objects)
            obj_name = ", ".join(obj_name_set)
        else:
            obj_name = best_match
        
        description_by_labels = get_description(given_labels, top_descriptive_labels)
        description = f"{color_name} {gender}'s {obj_name} {description_by_labels}"
        print(f"Image Description: {description}")
        
    elif(best_match == 'Bottom'):
        category = 1
        
        if(scores["Bottom"] == 1.0): #get the name of the object for the descriptiom
            obj_name_set = set(given_objects).intersection(bottom_objects)
            obj_name = ", ".join(obj_name_set)
        else:
            obj_name = best_match
            
        description_by_labels = get_description(given_labels, bottom_descriptive_labels)
        description = f"{color_name} {gender}'s {obj_name} {description_by_labels}"
        print(f"Image Description: {description}")
        
    else:
        category = 3
        
        if(scores["Shoe"] == 1):
            obj_name_set = set(given_objects).intersection(shoes_objects)
            obj_name = ", ".join(obj_name_set)
        else:
            obj_name = best_match
            
        description_by_labels = get_description(given_labels, shoe_descriptive_labels)
        description = f"{color_name} {gender}'s {obj_name} {description_by_labels}"
        print(f"Image Description: {description}")
        
    print("Category totals")
    for categories, score in scores.items():
        print(f"{categories}: {score}")
    
connection_string
    cnxn = pyodbc.connect(connection_string)

    # Create a cursor object to execute SQL queries
    cursor = cnxn.cursor()


    # Insert the data into the Clothing table
    insert_query = "INSERT INTO [dbo].[Clothing] (CategoryID, Gender, Color, Description, ImageURL, WardrobeID) VALUES (?, ?, ?, ?, ?, ?)"
    cursor.execute(insert_query, (category, gender, color_name, description, image_url, user.current_wardrobe))
    cnxn.commit()

    # Close the cursor and connection
    cursor.close()
    cnxn.close()
    

def imageProcess(image_url, gender):
    from google.cloud import vision
    print("Image processing started.")

    try:
        # Set the environment variable for service account credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'findathread-c2b11579a81c.json'

        # Authenticate the client
        client = vision.ImageAnnotatorClient()

        # Perform the desired Vision API tasks using the client
        
        image = vision.Image()
        image.source.image_uri = image_url

        # Perfom object detection
        response = client.object_localization(image=image)
        objects = response.localized_object_annotations
        detected_word =[obj.name.lower() for obj in objects]
        
        for word in detected_word:
            print(f"Object: {word}")
        
        # Perform label detection
        response = client.label_detection(image=image, max_results=50)
        labels = response.label_annotations

        # Print the labels for testing
        print("Labels:")
        for label in labels:
            print(label.description)

        # Extract dominant colors
        response = client.image_properties(image=image)
        dominant_colors = response.image_properties_annotation.dominant_colors.colors
        
        # Print the dominant colors for testing
        print("Dominant Colors:")
        color = dominant_colors[0].color
        color_rgb = (color.red, color.green, color.blue)
        
        color_name = get_color_name(color_rgb)
        
        imageToDatabase(detected_word, labels, image_url, color_name, gender)

        
        # Return any extracted information or perform further processing
    except Exception as e:
        # Print any errors that occur during authentication or API calls
        print(f"Error occurred during Vision API processing: {str(e)}")
        raise

    print("Image processing completed.")

@app.route('/upload', methods=['POST'])
def upload():

    file = request.files['file']
    #inputFile = Image.open(file)
    #ouputFile = remove(inputFile)
    gender = request.form['gender']
    print("GENDER SELCETED: " + gender.capitalize())
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
            imageProcess(image_url, gender)
            return jsonify({'status': 'duplicate'})  # Return duplicate image response
        else:
            # Upload the image
            blob_client.upload_blob(file)
            image_url = blob_client.url

            # Perform image processing on the uploaded image
            imageProcess(image_url, gender)
            return jsonify({'status': 'success'})

        return render_template('AddToWardrobe.html')
    else:
        return 'No file selected'
    
@app.route('/newWardrobe', methods=['POST'])
def newWardrobe():
    wardrobe_name = request.form.get('wardrobe-name')
     # Establish a connection to the database
connection_string
    cnxn = pyodbc.connect(connection_string)

    # # Create a cursor object to execute SQL queries
    cursor = cnxn.cursor()

    insert_query = "INSERT INTO [dbo].[Wardrobe] (ClothingID,wardrobeName,Stock) VALUES (?,?,?)"
    cursor.execute(insert_query, (None,wardrobe_name,None))
    

    query = "SELECT WardrobeID AS count FROM [dbo].[Wardrobe] WHERE [WardrobeName] = ?"
    cursor.execute(query, wardrobe_name)
    user.current_wardrobe =  cursor.fetchone()[0]
    
    insert_query = "INSERT INTO [dbo].[UserWardrobe] (UserID,WardrobeID) VALUES (?,?)"
    cursor.execute(insert_query, (user.current_user,user.current_wardrobe))
    cnxn.commit()
    # # Close the cursor and connection
    cursor.close()
    cnxn.close()
    existing_outfits = get_existing_outfits()
    return render_template('StartScreen.html',user=user,existing_outfits=existing_outfits)

@app.route('/selectWardrobe', methods=['POST'])
def selectWardrobe():
    wardrobe_id = request.form.get('existing-wardrobe')
    print (wardrobe_id)
    if wardrobe_id is not None:
        try:
            # Establish a connection to the database
        connection_string
            cnxn = pyodbc.connect(connection_string)

            # Create a cursor object to execute SQL queries
            cursor = cnxn.cursor()

            query = "SELECT WardrobeID AS count FROM [dbo].[Wardrobe] WHERE [WardrobeID] = ?"
            cursor.execute(query, wardrobe_id)
            result = cursor.fetchone()

            if result is not None:
                user.current_wardrobe = result[0]
                print(user.current_wardrobe)
                # Close the cursor and connection
                cursor.close()
                cnxn.close()
                existing_outfits = get_existing_outfits()
                return render_template('StartScreen.html',user=user, existing_outfits=existing_outfits)
            
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
        connection_string
            cnxn = pyodbc.connect(connection_string)

            # Create a cursor object to execute SQL queries
            cursor = cnxn.cursor()

            delete_query = "DELETE FROM [dbo].[UserWardrobe] WHERE [WardrobeID] = ?"
            cursor.execute(delete_query, wardrobe_id)    

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

@app.route('/delete_image', methods=['POST'])
def delete_image():
    try:
        image_url = request.json.get('imageURL')

        # Perform validation if needed (e.g., check if the imageURL is not empty)

        # Establish a connection to the database
    connection_string
        cnxn = pyodbc.connect(connection_string)

        # Create a cursor object to execute SQL queries
        cursor = cnxn.cursor()

        # Perform the delete operation using the image_url
        delete_query = "DELETE FROM [dbo].[Clothing] WHERE [ImageURL] = ?"
        cursor.execute(delete_query, image_url)
        cnxn.commit()

        # Close the cursor and connection
        cursor.close()
        cnxn.close()

        # Return a success response to the frontend
        return jsonify({'message': 'Image deleted successfully.'}), 200

    except Exception as e:
        # Handle any errors that occurred during database access
        return jsonify({'error': str(e)}), 500

@app.route('/head', methods=['GET', 'POST'])
def head():
    try:
    connection_string
        cnxn = pyodbc.connect(connection_string)

        cursor = cnxn.cursor()        
        category_id = 2

        cursor.execute(f"SELECT ImageURL, Gender, Color, Description, WardrobeID FROM Clothing WHERE CategoryId = {category_id} AND WardrobeID = {user.current_wardrobe}")
        rows = cursor.fetchall()

        # Extract the image URLs from the query results
        items_data = []
        
        for row in rows:
            item_data = {
                'imageURL': row.ImageURL,
                'gender': row.Gender,
                'color': row.Color,
                'description': row.Description
            }
            items_data.append(item_data)
        
        # Close the cursor and connection
        cursor.close()
        return render_template('head.html', items_data=items_data,outfit=outfit)
    except Exception as e:
        # Handle exceptions appropriately, e.g., log the error and return an error page
        print(f"Error: {e}")
        return render_template('error.html')

# Adjust the other methods similarly with the correct column name for 'Category'
# For example, if the column name is 'CategoryId' for 'tops':
@app.route('/tops', methods=['GET', 'POST'])
def tops():
    try:
    connection_string
        cnxn = pyodbc.connect(connection_string)

        cursor = cnxn.cursor()        
        category_id = 0

        cursor.execute(f"SELECT ImageURL, Gender, Color, Description, WardrobeID FROM Clothing WHERE CategoryId = {category_id} AND WardrobeID = {user.current_wardrobe}")
        rows = cursor.fetchall()

        # Extract the image URLs from the query results
        items_data = []
        
        for row in rows:
            item_data = {
                'imageURL': row.ImageURL,
                'gender': row.Gender,
                'color': row.Color,
                'description': row.Description
            }
            items_data.append(item_data)
        
        # Close the cursor and connection
        cursor.close()
        return render_template('Tops.html', items_data=items_data,outfit=outfit)
    except Exception as e:
        # Handle exceptions appropriately, e.g., log the error and return an error page
        print(f"Error: {e}")
        return render_template('error.html')

# Adjust the other methods similarly with the correct column name for 'Category'
# For example, if the column name is 'CategoryId' for 'tops':
@app.route('/bottoms', methods=['GET', 'POST'])
def bottoms():
    try:
    connection_string
        cnxn = pyodbc.connect(connection_string)

        cursor = cnxn.cursor()        
        category_id = 1

        cursor.execute(f"SELECT ImageURL, Gender, Color, Description, WardrobeID FROM Clothing WHERE CategoryId = {category_id} AND WardrobeID = {user.current_wardrobe}")
        rows = cursor.fetchall()

        # Extract the image URLs from the query results
        items_data = []
        
        for row in rows:
            item_data = {
                'imageURL': row.ImageURL,
                'gender': row.Gender,
                'color': row.Color,
                'description': row.Description
            }
            items_data.append(item_data)
        
        # Close the cursor and connection
        cursor.close()
        return render_template('bottoms.html', items_data=items_data,outfit=outfit)
    except Exception as e:
        # Handle exceptions appropriately, e.g., log the error and return an error page
        print(f"Error: {e}")
        return render_template('error.html')
    
# Adjust the other methods similarly with the correct column name for 'Category'
# For example, if the column name is 'CategoryId' for 'tops':
@app.route('/shoes', methods=['GET', 'POST'])
def shoes():
    try:
    connection_string
        cnxn = pyodbc.connect(connection_string)

        cursor = cnxn.cursor()        
        category_id = 3

        cursor.execute(f"SELECT ImageURL, Gender, Color, Description, WardrobeID FROM Clothing WHERE CategoryId = {category_id} AND WardrobeID = {user.current_wardrobe}")
        rows = cursor.fetchall()

        # Extract the image URLs from the query results
        items_data = []
        
        for row in rows:
            item_data = {
                'imageURL': row.ImageURL,
                'gender': row.Gender,
                'color': row.Color,
                'description': row.Description
            }
            items_data.append(item_data)
        
        # Close the cursor and connection
        cursor.close()
        return render_template('shoes.html', items_data=items_data, outfit=outfit)
    except Exception as e:
        # Handle exceptions appropriately, e.g., log the error and return an error page
        print(f"Error: {e}")
        return render_template('error.html')

# Route to display the form to set the head image URL
@app.route('/set_head', methods=['POST'])
def set_head():
    head_image_url = request.form.get('selectedHeadImage')
    outfit.user_head = head_image_url
    flash("Top image URL set successfully: " + head_image_url, "success")
    return redirect(url_for('create_outfit'))  # Redirect to the appropriate route

# Route to display the form to set the top image URL
@app.route('/set_top', methods=['POST'])
def set_top():
    top_image_url = request.form.get('selectedTopImage')
    outfit.user_top = top_image_url
    flash("Top image URL set successfully: " + top_image_url, "success")
    return redirect(url_for('create_outfit'))

# Route to display the form to set the bottom image URL
@app.route('/set_bottom', methods=['POST'])
def set_bottom():
    bottom_image_url = request.form.get('selectedBottomImage')
    outfit.user_bottom = bottom_image_url
    flash("Bottom image URL set successfully: " + bottom_image_url, "success")
    return redirect(url_for('create_outfit'))

# Route to display the form to set the shoes image URL
@app.route('/set_shoes', methods=['POST'])
def set_shoes():
    shoes_image_url = request.form.get('selectedShoesImage')
    outfit.user_shoes = shoes_image_url
    flash("Shoes image URL set successfully: " + shoes_image_url, "success")
    return redirect(url_for('create_outfit'))

# Route to display the outfit creation form
@app.route('/create_outfit')
def create_outfit():
    return render_template('CreateAnOutfit.html', outfit=outfit)

@app.route('/saveOutfit', methods=['POST'])
def saveOutfit():
    outfit_name = request.form.get('outfit-name')

     # Establish a connection to the database
connection_string
    cnxn = pyodbc.connect(connection_string)

    # # Create a cursor object to execute SQL queries
    cursor = cnxn.cursor()

    insert_query = "INSERT INTO [dbo].UserOutfits (UserID, OutfitName, Head, Tops, Bottom, Shoes) VALUES (?,?,?,?,?,?)"
    cursor.execute(insert_query, (user.current_user,outfit_name,outfit.user_head,outfit.user_top,outfit.user_bottom,outfit.user_shoes))
    cnxn.commit()

    # # Close the cursor and connection
    cursor.close()
    cnxn.close()

    return render_template('CreateAnOutfit.html',outfit=outfit,user=user)

def get_existing_outfits():
    # Establish a connection to the database
connection_string
    conn = pyodbc.connect(connection_string)

    # Execute the query to retrieve existing wardrobe IDs and names
    cursor = conn.cursor()
    cursor.execute("SELECT OutfitID, OutfitName FROM UserOutfits WHERE UserID = ?", user.current_user)
    rows = cursor.fetchall()

    # Create a list of dictionaries with wardrobe IDs and names
    existing_outfits = [{'id': row[0], 'name': row[1]} for row in rows]

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print(existing_outfits)
    return existing_outfits

@app.route('/loadOutfit', methods=['POST'])
def loadOutfit():
    outfit_id = request.form.get('existing-outfits')
    print (outfit_id)
    if outfit_id is not None:
        try:
            # Establish a connection to the database
        connection_string
            cnxn = pyodbc.connect(connection_string)

            # Create a cursor object to execute SQL queries
            cursor = cnxn.cursor()

            query = "SELECT OutfitName,Head,Tops,Bottom,Shoes AS count FROM [dbo].[UserOutfits] WHERE [OutfitID] = ?"
            cursor.execute(query, outfit_id)
            result = cursor.fetchone()

            if result is not None:
                current_outfit = result[0]
                outfit.user_head = result[1]
                outfit.user_top = result[2]
                outfit.user_bottom = result[3]
                outfit.user_shoes = result[4]
                print(current_outfit)
                # Close the cursor and connection
                cursor.close()
                cnxn.close()
                return render_template('CreateAnOutfit.html',outfit = outfit)
            
            # Handle the case where no records were found
            return 'No Outfits found with the specified name'
        
        except Exception as e:
            # Handle any errors that occurred during database access
            return f'Error accessing the database: {str(e)}'
    
    # Handle the case where the wardrobe_name is None
    return 'Failed to select outfit'

@app.route('/deleteOutfit', methods=['POST'])
def deleteOutfit():
    outfit_id = request.form.get('delete-outfit')
    
    if outfit_id is not None:
        try:
            # Establish a connection to the database
        connection_string
            cnxn = pyodbc.connect(connection_string)

            # Create a cursor object to execute SQL queries
            cursor = cnxn.cursor()

            # Perform the delete operation using the wardrobe_id
            delete_query = "DELETE FROM [dbo].[UserOutfits] WHERE [OutfitID] = ?"
            cursor.execute(delete_query, outfit_id)
            cnxn.commit()

            # Close the cursor and connection
            cursor.close()
            cnxn.close()
            existing_wardrobes = get_existing_wardrobes()
            return render_template('AddToWardrobe.html', existing_wardrobes=existing_wardrobes)
        
        except Exception as e:
            # Handle any errors that occurred during database access
            return f'Error accessing the database: {str(e)}'
    
    # Handle the case where the wardrobe_id is None
    return 'Failed to delete outfit'