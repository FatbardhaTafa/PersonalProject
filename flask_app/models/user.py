from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class User:
    DB = "recipes_project"
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password= data['password']
        self.confirm_password= data['confirm_password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
    @classmethod
    def create(cls,data):
        query="INSERT INTO users (first_name, last_name, email, password, confirm_password) VALUES ( %(first_name)s, %(last_name)s, %(email)s, %(password)s, %(confirm_password)s);"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def get_user_by_email(cls,data):
        query= 'SELECT * FROM users WHERE email= %(email)s;'
        result= connectToMySQL(cls.DB).query_db(query, data)
        if result:
            return result[0]
        return False
    

    @staticmethod
    def validate_userRegister(user):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!", 'emailRegister')
            is_valid = False

        if len(user['password']) <= 1:
            flash("Password is required!", 'passwordRegister')
            is_valid = False
        elif not any(char.isdigit() for char in user['password']):
            flash("Password must contain at least 1 number!", 'passwordRegister')
            is_valid = False
        elif not any(char.isupper() for char in user['password']):
            flash("Password must contain at least 1 uppercase letter!", 'passwordRegister')
            is_valid = False
            
        if len(user['confirm_password'])<=1 or user['confirm_password'] != user['password']:
            flash("Confirm password is incorrect!", 'passwordConfirm')
            is_valid = False
        if len(user['first_name'])<2:
            flash("First name is required!", 'nameRegister')
            is_valid = False
        if len(user['last_name'])<2:
            flash("Last name is required!", 'lastNameRegister')
            is_valid = False
        return is_valid

    @staticmethod
    def validate_user(user):
        is_valid= True
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!", 'emailLogin')
            is_valid = False
        if len(user['password'])<1:
            flash("Password is required!", 'passwordLogin')
            is_valid = False
        return is_valid
    

    @classmethod
    def get_user_by_id(cls, user_id):
        query = 'SELECT * FROM users WHERE id = %(id)s;'
        data = {'id': user_id}
        result = connectToMySQL(cls.DB).query_db(query,data)
        return result[0]
