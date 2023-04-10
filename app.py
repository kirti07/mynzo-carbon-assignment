import random
import logging
import math
import os
import json
from validate_email import validate_email
from flask import Flask, request, jsonify, make_response,render_template
from pymongo import MongoClient

app = Flask(__name__)
config = open(os.path.join(os.path.dirname(__file__), 'config', 'config.json'))
config_data = json.load(config)
config.close()


#User Model
class UserDetail:
    """
    User model for information pertainig to a user

    """
    def __init__(self,email):
        self.email = email
        self.first_name = ""
        self.last_name = ""
        self.city = ""
        self.state = ""
        self.country = ""
        self.photo = None

    def create_profile(self):
        """If the email does not exists in the database ,
        this will fill up all the information for user
        """
        first_name = request.json.get('firstName')
        last_name = request.json.get('lastName')
        city = request.json.get('City')
        state = request.json.get('State')
        country = request.json.get('Country')
        photo = request.files.get('Photo')
        photo_filename = None
        if photo and photo.content_length < 50 * 1024 * 1024:
            photo_filename = photo.filename
            photo.save('Some Storage')
        if self.is_valid_schema(city, state, country):
            self.first_name = first_name
            self.last_name = last_name
            self.city = city
            self.state = state
            self.country= country
            self.photo = photo_filename
        else:
            return jsonify({'error':'Invalid City, State or Country'}, 400)

    def update_user_profile(self):
        """Updates information which are not empty
        """
        first_name = request.json.get('firstName')
        last_name = request.json.get('lastName')
        city = request.json.get('City')
        state = request.json.get('State')
        country = request.json.get('Country')
        
        if first_name:
            self.first_name = request.json.get(first_name)
        if last_name:
            self.last_name = request.json.get(last_name)
        if self.is_valid_schema(city,state,country):
            self.city = city
            self.state=state
            self.country=country
        photo = request.files.get('Photo')
        if photo and photo.content_length < 50 * 1024 *1024:
            photo.save('Some Storage')
            self.photo = photo.filename    
    def is_valid_schema(self,city,state,country):
        """ Verify the city and state provided by the user is correct
        """
        cursor = cities.find_one({'name':city, 'state':state, 'country':country})
        if not cursor:
            return False
        return True

    
client = MongoClient(config_data['CONNECTION_STRING'])
db = client['admin']
users = db.userInformation
cities = db.cities

def generate_otp():
    """ random 6 digit OTP generation
    returns otp
    """
    otp = ""
    for _ in range(6):
        otp += str(math.floor(random.random() * 10))
    return otp

@app.route('/api/login', methods = ['POST'])
def send_otp():
    """ Login/SignUp,
    1.  check if the database connection is established and table is present
    2. gets the email as user response
    3. calls otp generator
    4. if signup - create user profile in the db
    5. prints otp. 
    """
    email = request.json.get('email')
    if not validate_email(email):
        return make_response(jsonify({'message':'Invalid Email'}), 403)

    otp = generate_otp()
    if users.count_documents({"email":email}) <= 0:
        print("Welcome to our App, please create your user profile")
        new_user = UserDetail(email)
        new_user.create_profile()
        new_user_record = new_user.__dict__
        users.insert_one(new_user_record)
    otp = generate_otp()
    print(f"OTP for {email}:{otp}")
    return make_response(jsonify({"message: 'OTP sent successfully"}), 200)

@app.route('/api/updateprofile', methods=['PUT'])
def update_profile():
    """
    Inputs the email
    if email not present in the database returns
    asks for the fields to be updated. 
    updates the field
    """
    email = request.json.get('email')
    # users = get_table_details()
    user_to_update = users.find_one({'email':email})
    if not user_to_update:
        return make_response(jsonify({'error':'User not found'}), 400)
    updated_user = UserDetail(email)
    updated_user.update_user_profile()
    users.update_one({'email':email}, {'$set': updated_user.__dict__})
    return jsonify(updated_user), 200

@app.route('/profile', methods = ['GET'])
def view_profile():
    """Checks if the user profile is created in database.
     if created then the user information will be rendered in the format displayed in profile.html
    """
    email = request.args.get('email')
    user = users.find_one({'email':email})
    if not user:
        return jsonify({'error':'User not found'}, 404)
    return render_template('profile.html',user=user)