from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models.user import User


class Recipe:
    DB = "recipes_project"
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.instructions = data['instructions']
        self.under_30= data['under_30']
        self.difficulty_level = data['difficulty_level']
        self.ingredients= data['ingredients']
        self.calories= data['calories']
        self.notes= data['notes']
        self.photo= data['photo']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user= data['user']


    @classmethod
    def get_all(cls):
        query='SELECT * FROM recipes JOIN users ON recipes.user_id=users.id ORDER BY recipes.created_at DESC;'
        results= connectToMySQL(cls.DB).query_db(query)
        all_recipes=[]
        for result in results:
            recipe_user=  User({
                'id': result['user_id'],
                'email': result['email'],
                'first_name': result['first_name'],
                'last_name': result['last_name'],
                'created_at': result['users.created_at'],
                'updated_at': result['users.updated_at'],
                'password': result['password'],
                'confirm_password': result['confirm_password']
            })
            new_recipe= Recipe({
                'id': result['id'],
                'name': result['name'],
                'description': result['description'],
                'instructions': result['instructions'],
                'under_30': result['under_30'],
                'difficulty_level': result['difficulty_level'],
                'ingredients': result['ingredients'],
                'calories': result['calories'],
                'notes': result['notes'],
                'photo': result['photo'],
                'created_at': result['created_at'],
                'updated_at': result['updated_at'],
                'user': recipe_user
            })
            all_recipes.append(new_recipe)
        return all_recipes
    

    @classmethod
    def save(cls,data):
        query='INSERT INTO recipes (name, description, instructions, under_30, difficulty_level ,ingredients ,calories , notes , photo, user_id) values (%(name)s, %(description)s, %(instructions)s, %(under_30)s, %(difficulty_level)s,%(ingredients)s,%(calories)s,%(notes)s,%(photo)s, %(user_id)s);'
        result= connectToMySQL(cls.DB).query_db(query,data)
        return result
    
    @classmethod
    def update_profile(cls, data):
        query = "UPDATE recipes set photo = %(photo)s WHERE id = %(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def get_recipe_by_id(cls,data):
        query="SELECT * FROM recipes LEFT JOIN users ON recipes.user_id=users.id WHERE recipes.id=%(id)s;"
        result= connectToMySQL(cls.DB).query_db(query,data)
        if result:
            comments = []

            query2 = "SELECT * FROM comments left join users on comments.user_id = users.id where comments.recipe_id = %(id)s;"
            result2 = connectToMySQL(cls.DB).query_db(query2, data)
            if result2:
                for comment in result2:
                    comments.append(comment)
            result[0]['commentss'] = comments
            query3 = "SELECT users.first_name, users.last_name FROM likes left join users on likes.user_id = users.id where likes.recipe_id = %(id)s;"
            result3 = connectToMySQL(cls.DB).query_db(query3, data)
            likes = []
            if result3:
                for like in result3:
                    likes.append(like)
            result[0]['likes'] = likes
            return result[0]
        return False
    
    @classmethod
    def update(cls,data):
        query="UPDATE recipes SET name=%(name)s, description= %(description)s, instructions= %(instructions)s, under_30=%(under_30)s , difficulty_level= %(difficulty_level)s, ingredients= %(ingredients)s,calories= %(calories)s,notes= %(notes)s,photo= %(photo)s WHERE recipes.id=%(id)s;"
        return connectToMySQL(cls.DB).query_db(query,data)
    
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM recipes where id = %(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def delete_all_recipe_comments(cls, data):
        query ="DELETE FROM comments where comments.recipe_id = %(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @staticmethod
    def validate_recipe_content(recipe):
        is_valid= True
        if len(recipe['name'])<3:
            flash('Recipe name must be at least 3 characters', 'nameRecipe')
            is_valid=False
        if len(recipe['description'])<3:
            flash('You should put a valid description for recipe', 'descriptionRecipe')
            is_valid=False
        if len(recipe['instructions'])<3:
            flash('Involve some instructions for your recipe', 'instructionsRecipe')
            is_valid=False
        if len(recipe['notes'])<3:
            flash('Involve some notes for your recipe', 'notesRecipe')
            is_valid=False
        return is_valid
    
    
    @staticmethod
    def validate_update_recipe_content(recipe):
        is_valid= True
        if len(recipe['name'])<3:
            flash('Recipe name must be at least 3 characters', 'nameRecipe')
            is_valid=False
        if len(recipe['description'])<3:
            flash('You should put a valid description for recipe', 'descriptionRecipe')
            is_valid=False
        if len(recipe['instructions'])<3:
            flash('Involve some instructions for your recipe', 'instructionsRecipe')
            is_valid=False
        if len(recipe['notes'])<3:
            flash('Involve some notes for your recipe', 'notesRecipe')
            is_valid=False
        return is_valid

    # metoda per comments
    @classmethod
    def add_comment(cls,data):
        query='INSERT INTO comments (comment, user_id, recipe_id) VALUES (%(comment)s, %(user_id)s, %(recipe_id)s);'
        return connectToMySQL(cls.DB).query_db(query,data)
    
    @classmethod
    def get_comment_by_id(cls,data):
        query= 'SELECT* FROM comments WHERE comments.id=%(id)s;'
        results= connectToMySQL(cls.DB).query_db(query,data)
        if results:
            return results[0]
        return False
    
    @classmethod
    def deleteComment(cls,data):
        query='DELETE FROM comments WHERE id=%(id)s;'
        return connectToMySQL(cls.DB).query_db(query,data)
    
    @classmethod
    def delete_all_recipe_comments(cls, data):
        query ="DELETE FROM comments where comments.recipe_id = %(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def update_comment(cls, data):
        query = "UPDATE comments set comment = %(comment)s where id = %(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)

    
    
    #methods for likes

    @classmethod
    def addLike(cls, data):
        query = "INSERT INTO likes (user_id, recipe_id) VALUES (%(user_id)s, %(recipe_id)s);"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def removeLike(cls, data):
        query = "DELETE FROM likes WHERE recipe_id=%(recipe_id)s AND user_id = %(user_id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def delete_all_recipe_like(cls, data):
        query ="DELETE FROM likes where likes.recipe_id = %(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    
    @classmethod
    def get_users_who_liked_by_recipe_id(cls, data):
        query ="SELECT * FROM likes where recipe_id = %(recipe_id)s;"
        results = connectToMySQL(cls.DB).query_db(query, data)
        usersId = []
        if results:
            for userId in results:
                usersId.append(userId['user_id'])
        return usersId
    
    @classmethod
    def get_liked_recipes_by_user_id(cls, user_id):
        query = "SELECT * FROM recipes WHERE id IN (SELECT recipe_id FROM likes WHERE user_id = %s)"
        return  connectToMySQL(cls.DB).query_db(query, (user_id,))


    # @classmethod
    # def search_by_name(cls, query):
    #     query = "SELECT * FROM recipes WHERE name LIKE %s ORDER BY created_at DESC;"
    #     results = connectToMySQL(cls.DB).query_db(query, ('%' + query + '%',))
    #     if results:
    #         all_recipes = []
    #         for result in results:
    #             new_recipe = Recipe(result)  # Assuming you have a constructor that creates Recipe objects
    #             all_recipes.append(new_recipe)
    #         return all_recipes
    #     return []
    
    
    # @classmethod
    # def search_by_name(cls, query):
    #     query = "SELECT * FROM recipes JOIN users ON recipes.user_id=users.id WHERE name LIKE %s ORDER BY recipes.created_at DESC;"
    #     results = connectToMySQL(cls.DB).query_db(query, ('%' + query + '%',))
    #     if results:
    #         all_recipes = []
    #         for result in results:
    #             recipe_user = User({
    #                 'id': result['user_id'],
    #                 'email': result['email'],
    #                 'first_name': result['first_name'],
    #                 'last_name': result['last_name'],
    #                 'created_at': result['users.created_at'],
    #                 'updated_at': result['users.updated_at'],
    #                 'password': result['password'],
    #                 'confirm_password': result['confirm_password']
    #             })
    #             new_recipe = Recipe({
    #                 'id': result['id'],
    #                 'name': result['name'],
    #                 'description': result['description'],
    #                 'instructions': result['instructions'],
    #                 'under_30': result['under_30'],
    #                 'difficulty_level': result['difficulty_level'],
    #                 'ingredients': result['ingredients'],
    #                 'calories': result['calories'],
    #                 'notes': result['notes'],
    #                 'photo': result['photo'],
    #                 'created_at': result['created_at'],
    #                 'updated_at': result['updated_at'],
    #                 'user': recipe_user
    #             })
    #             all_recipes.append(new_recipe)
    #         return all_recipes
    #     return []