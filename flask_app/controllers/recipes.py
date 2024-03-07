import csv
from email.mime.text import MIMEText
from io import StringIO
import smtplib
from flask_app import app
from flask import make_response, render_template, redirect, request, session, flash
from flask_app.models.recipe import Recipe
from flask_app.models.user import User

from io import StringIO
import csv
from flask import make_response
import os
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
from datetime import datetime
from urllib.parse import unquote
UPLOAD_FOLDER = 'flask_app/static/images'
ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif','webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/recipes/new')
def addRecipe():
    if 'user_id' in session:
        return render_template('addRecipe.html')
    return redirect('/')

@app.route('/all/recipes')
def allRecipes():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.get_user_by_id(user_id)
        if user:
            recipes = Recipe.get_all()  
            return render_template('allRecipe.html', user=user, recipes=recipes)
    return redirect('/')


@app.route('/recipes/new', methods=['GET', 'POST'])
def create_or_update_recipe():
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect('/') 
        return render_template('addRecipe.html')

    elif request.method == 'POST':
        if 'user_id' not in session:
            return redirect('/') 
        if not Recipe.validate_recipe_content(request.form):
            return redirect(request.referrer)
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
            else:
                flash('Invalid file format', 'error')
                return redirect(request.referrer)
        else:
            flash('No file part', 'error')
            return redirect(request.referrer)
        data = {
            'name': request.form['name'],
            'description': request.form['description'],
            'instructions': request.form['instructions'],
            'under_30': request.form['under_30'],
            'difficulty_level': request.form['difficulty_level'],
            'ingredients': request.form['ingredients'],
            'calories': request.form['calories'],
            'notes': request.form['notes'],
            'photo': filename, 
            'user_id': session['user_id']
        }
        Recipe.save(data)
        flash('Recipe added successfully!', 'success')
        return redirect('/')
    return redirect('/')

# @app.route('/recipes/new', methods=['GET', 'POST'])
# def create_or_update_recipe():
#     if request.method == 'GET':
#         if 'user_id' not in session:
#             return redirect('/') 
#         return render_template('addRecipe.html')

#     elif request.method == 'POST':
#         if 'user_id' not in session:
#             return redirect('/') 
#         if not Recipe.validate_recipe_content(request.form):
#             return redirect(request.referrer)
        
#         # Save the uploaded photos to the server
#         photos = request.files.getlist('photos')
#         filenames = []
#         for photo in photos:
#             if photo.filename != '' and allowed_file(photo.filename):
#                 filename = secure_filename(photo.filename)
#                 file_path = os.path.join(UPLOAD_FOLDER, filename)
#                 photo.save(file_path)
#                 filenames.append(filename)
#             else:
#                 flash('Invalid file format', 'error')
#                 return redirect(request.referrer)
        
#         data = {
#             'name': request.form['name'],
#             'description': request.form['description'],
#             'instructions': request.form['instructions'],
#             'under_30': request.form['under_30'],
#             'difficulty_level': request.form['difficulty_level'],
#             'ingredients': request.form['ingredients'],
#             'calories': request.form['calories'],
#             'notes': request.form['notes'],
#             'photos': filenames,  # Save list of filenames
#             'user_id': session['user_id']
#         }
#         Recipe.save(data)
#         flash('Recipe added successfully!', 'success')
#         return redirect('/')
#     return redirect('/')

   
@app.route('/recipes/show/<int:id>')
def show_recipes(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': id
    }
    recipe = Recipe.get_recipe_by_id(data)
    commenti = Recipe.get_comment_by_id
    if recipe:
        return render_template('detail.html', commenti=commenti, recipe=recipe)
    return redirect('/')

@app.route('/recipes/edit/<int:id>')
def edit_recipes(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': id
    }
    recipe = Recipe.get_recipe_by_id(data)
    if recipe and recipe['user_id'] == session['user_id']:
        return render_template('editRecipe.html', recipe=recipe)
    return redirect('/')

@app.route('/recipes/edit/<int:id>', methods=['POST'])
def update_recipe(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': id
    }
    recipe = Recipe.get_recipe_by_id(data)
    if  recipe['user_id'] == session['user_id']:
        if not Recipe.validate_update_recipe_content(request.form):
            return redirect(request.referrer)
        data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'instructions': request.form.get('instructions'),
            'under_30': request.form.get('under_30'),
            'difficulty_level': request.form.get('difficulty_level'),
            'ingredients': request.form.get('ingredients'),
            'calories': request.form.get('calories'),
            'notes': request.form.get('notes'),
            'photo': request.form.get('photo'),
            'id': id
        }
        Recipe.update(data)
        return redirect('/all/recipes')
    return redirect('/')

@app.route('/recipes/delete/<int:id>')
def delete_recipe(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': id,
    }
    recipe = Recipe.get_recipe_by_id(data)
    if recipe['user_id'] == session['user_id']:
        Recipe.delete_all_recipe_comments(data)
        Recipe.delete_all_recipe_like(data)
        Recipe.delete(data)
    return redirect(request.referrer)

# route for comments

@app.route('/comments/show/<int:id>')
def show_comments(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': id
    }
    recipe = Recipe.get_recipe_by_id(data)
    commenti = Recipe.get_comment_by_id 
    if recipe:
        return render_template('detail.html', recipe=recipe, commenti=commenti)
    return redirect('/')

@app.route('/add/comment/<int:id>', methods=['POST'])
def addComment(id):
    if 'user_id' not in session:
        return redirect('/')
    if len(request.form['comment']) < 2:
        flash('The comment should be at least two characters', 'comment')
        return redirect(request.referrer)
    data = {
        'comment': request.form['comment'],
        'user_id': session['user_id'],
        'recipe_id': id
    }
    Recipe.add_comment(data)
    return redirect(request.referrer)

@app.route('/delete/comment/<int:id>')
def deleteComment(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': id
    }
    comment = Recipe.get_comment_by_id(data)
    if comment and comment['user_id'] == session['user_id']:
        Recipe.deleteComment(data)
    return redirect(request.referrer)


# route for likes

@app.route('/add/like/<int:id>')
def addLike(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'user_id': session['user_id'],
        'recipe_id': id
    }
    Recipe.addLike(data)
    return redirect(request.referrer)


@app.route('/remove/like/<int:id>')
def removeLike(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'user_id': session['user_id'],
        'recipe_id': id
    }
    Recipe.removeLike(data)
    return redirect(request.referrer)


@app.context_processor
def utility_processor():
    def get_likes_count(recipe_id):
        data = {'recipe_id': recipe_id}
        usersWhoLikes = Recipe.get_users_who_liked_by_recipe_id(data)
        return len(usersWhoLikes)
    def get_users_who_liked(recipe_id):
        data = {'recipe_id': recipe_id}
        usersWhoLiked = Recipe.get_users_who_liked_by_recipe_id(data)
        return usersWhoLiked
    return {'get_likes_count': get_likes_count, 'get_users_who_liked': get_users_who_liked}


@app.route('/favourite')
def favourite():
    if 'user_id' not in session:
        return redirect('/')
    user_id = session['user_id']
    liked_recipe_ids = Recipe.get_liked_recipes_by_user_id(user_id)
    liked_recipes = []
    for recipe_id in liked_recipe_ids:
        recipe_data = {
            'id': recipe_id['id']
        }
        recipe = Recipe.get_recipe_by_id(recipe_data)
        if recipe:
            liked_recipes.append(recipe)
    if 'get_liked_recipes_by_user_id' in session:
        new_recipe_id = session.pop('get_liked_recipes_by_user_id')
        recipe_data = {
            'id': new_recipe_id
        }
        new_recipe = Recipe.get_recipe_by_id(recipe_data)
        if new_recipe:
            liked_recipes.insert(0, new_recipe)
    
    return render_template('favourite.html', liked_recipes=liked_recipes)

@app.route('/download')
def download():
    recipes = Recipe.get_all()  
    output = StringIO()  
    writer = csv.writer(output)  

    for recipe in recipes:
        writer.writerow(['Name', recipe.name])
        writer.writerow(['Description', recipe.description])
        writer.writerow(['Instructions', recipe.instructions])
        writer.writerow(['Difficulty Level', recipe.difficulty_level])
        writer.writerow(['Ingredients', recipe.ingredients])
        writer.writerow(['Under 30 Minutes', recipe.under_30])
        writer.writerow(['Calories', recipe.calories])
        writer.writerow(['Notes', recipe.notes])
        writer.writerow([])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=recipes.csv'
    return response



@app.route('/download/recipe/<int:id>')
def download_recipe(id):
    data = {
        'id': id
    }
    recipe = Recipe.get_recipe_by_id(data) 
    if not recipe:
        return "Recipe not found", 404
    output = StringIO()  
    writer = csv.writer(output) 

    writer.writerow(['Name', recipe['name']])
    writer.writerow(['Description', recipe['description']])
    writer.writerow(['Instructions', recipe['instructions']])
    writer.writerow(['Difficulty Level', recipe['difficulty_level']])
    writer.writerow(['Ingredients', recipe['ingredients']])
    writer.writerow(['Under 30 Minutes', recipe['under_30']])
    writer.writerow(['Calories', recipe['calories']])
    writer.writerow(['Notes', recipe['notes']])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={recipe['name']}.csv'
    return response

@app.route('/about')
def about():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('about.html')

@app.route('/contact')
def contact():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('contact.html')

# @app.route('/search', methods=['GET'])
# def search_recipes():
#     query = request.args.get('q')  # Get the search query from the URL parameter
#     if query:
#         # Perform a search query in the database for recipes containing the search query in their name
#         recipes = Recipe.search_by_name(query)
#         return render_template('allRecipe.html', recipes=recipes, query=query)
#     else:
#         # If no search query is provided, redirect to the homepage or display an error message
#         flash('Please enter a search query.', 'error')
#         return redirect(request.referrer)



