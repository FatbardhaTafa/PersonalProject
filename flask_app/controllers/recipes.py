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




# Data for recipe suggestions
recipes = [
    {
        "title": "Pite me Mish",
        "description": "Pite tradicionale shqiptare me mish dhe perime.",
        "image": "https://travelfoodatlas.com/wp-content/uploads/2023/11/Pite-Me-Mish.jpg",
        "url": "https://www.youtube.com/watch?v=RGr66fpnJ5w"
    },
    {
        "title": "Tavë Kosi",
        "description": "Recetë e thjeshtë dhe e shijshme e tavës së kosit.",
        "image": "https://www.mygoldenpear.com/wp-content/uploads/Tave-Kosi-recipe-joghurt.jpg",
        "url": "https://www.youtube.com/results?search_query=tave+kosi"
    },
    {
        "title": "Flija",
        "description": "Recetë tradicionale shqiptare e ëmbël dhe e shijshme.",
        "image": "https://www.artigatimit.com/wp-content/uploads/2017/02/flija-receta-gatimi-kuzhina-kosovare.jpg",
        "url": "https://www.google.com/search?q=flija&rlz=1C1KNTJ_enAL1033AL1033&oq=flija&gs_lcrp=EgZjaHJvbWUqCggAEAAY4wIYgAQyCggAEAAY4wIYgAQyBwgBEC4YgAQyBwgCEAAYgAQyBwgDEAAYgAQyBwgEEAAYgAQyBwgFEAAYgAQyBwgGEAAYgAQyBwgHEAAYgAQyDwgIEC4YChjHARjRAxiABDIHCAkQABiABNIBCDUyNzlqMGo0qAIIsAIB&sourceid=chrome&ie=UTF-8#fpstate=ive&vld=cid:e90debb3,vid:1fPmnJREVVM,st:0"
    },
    {
        "title": "Byrek me Mish",
        "description": "Byrek tradicional shqiptar me mish dhe përime.",
        "image": "https://media.sot.com.al/sot.com.al/media/-800-0-5fdc2fe672af888bdc20f425baa00461.jpg",
        "url": "https://www.youtube.com/watch?app=desktop&v=sM92rYfs9iM"
    },
    {
        "title": "Qofte të Fërguara",
        "description": "Qofte të shijshme te bera plot dashuri dhe  të pjekura në furrë.",
        "image": "https://www.myalbanianfood.com/wp-content/uploads/2017/03/Albanian-Qofte-1300x731.jpg",
        "url": "https://www.youtube.com/watch?v=4-m9U4R013c"
    },
    {
        "title": "Speca të Mbushur",
        "description": "Speca të mbushur me mish dhe oriz, një pjatë e shijshme dhe e shëndetshme.",
        "image": "https://unegatuaj.com/wp-content/uploads/2014/07/Speca-te-mbushur.jpg",
        "url": "https://www.youtube.com/watch?v=003_vvubQz8"
    },
    {
        "title": "Trileçe",
        "description": "Trileçe është një embëlsirë e përbërë prej tre lloje mishi dhe e shtruar me sheqer dhe qumësht të kondensuar.",
        "image": "https://photo.foodgawker.com/wp-content/uploads/2021/11/3778230.jpg",
        "url": "https://www.youtube.com/watch?v=J7CkpI62OnU"
    },
    {
        "title": "Revani",
        "description": "Revani është një embëlsirë tradicionale shqiptare e përgatitur me miell, sheqer, qumësht dhe hudhër.",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcStOTJxDe2ZHW5efCLHWst9uWI1-jhGG6IuatYNhgqokA&s",
        "url": "https://www.youtube.com/watch?v=KtRA5Xz9OAw"
    },
    {
        "title": "Bakllava",
        "description": "Bakllava është një embëlsirë e njohur, e përgatitur me fleta të holla të brumëzura dhe të mbushura me arra të grira .",
        "image": "https://www.artigatimit.com/wp-content/uploads/2020/12/bakllava-arra-receta-tradicionale-shqiptare-artigatimit-500x500.jpg",
        "url": "https://www.youtube.com/watch?v=D8RliYObRwU"
    },
    {
        "title": "Kungull me Oriz",
        "description": "Kungulli i mbushur me oriz dhe perime është një zgjedhje e shijshme dhe e shëndetshme për sezonin e vjeshtës.",
        "image": "https://gati.me/images/cropped-kunguj.PNG",
        "url": "https://www.youtube.com/watch?v=LCQdnlEIweA"
    },
    {
        "title": "Ballokume",
        "description": "Ballokume është një embëlsirë tradicionale shqiptare e pjekur me miell, mjaltë dhe gjalpë.",
        "image": "https://travelfoodatlas.com/wp-content/uploads/2021/06/Ballokume.jpg",
        "url": "https://www.youtube.com/watch?v=rHaG_eghlyY"
    },
    {
    "title": "Tiramisu",
    "description": "Tiramisu është një embëlsirë italiane e shijshme, e përgatitur me keksa, kafe, krem mascarpone dhe kakaon e pluhur.",
    "image": "https://www.gimmesomeoven.com/wp-content/uploads/2020/07/Tiramisu-Recipe-Cover.jpg",
    "url": "https://youtube.com/watch?v=7VTtenyKRg4"
    },
    {
        "title": "Tave Dheu",
        "description": "Tavë Dheu është një pjatë tradicionale shqiptare e përgatitur me mish të pjekur, perime dhe mjaltë.",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTFoCn7ATyOsBcl67ZlYLiXyFuDSWuJ2UqWafXw1awFwg&s",
        "url": "https://www.youtube.com/watch?v=eUeBi_kZ5lo"
    },
    {
        "title": "Fergesë",
        "description": "Fergesë është një pjatë e thjeshtë dhe e shijshme me spec të kuq, domate, dhe djathë.",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBLRHPjoNsPXA4xaffpcylBEUUxFvJIrz4vQBW6NUuMg&s",
        "url": "https://www.youtube.com/watch?v=1DJojddai2o"
    },
    {
        "title": "Pite me Gjize",
        "description": "Pite me Gjize është një pite dhe ushqim  tradicionale shqiptare e përgatitur me gjizë dhe veze.",
        "image": "https://i.ytimg.com/vi/jUpqyVCTsrY/maxresdefault.jpg",
        "url": "https://www.youtube.com/watch?v=s47LgEipo8c"
    },
    {
        "title": "Japrak",
        "description": "Japrak janë gjethe të pjekura me një mbushje të përzier me oriz dhe mish të pjekur, shpesh të servirura me qumësht .",
        "image": "https://www.artigatimit.com/wp-content/uploads/2016/05/receta-gatimi-japrak-kuzhina-shqiptare-artigatimit-shqip-shije.jpg",
        "url": "https://www.youtube.com/watch?v=nycD_M-Cm40"
    },
     {
        "title": "Tavë Kosi me Mish",
        "description": "Tavë Kosi me Mish është një version i tavës së kosit me shtimin e mishit të pjekur në furrë.",
        "image": "https://i.ytimg.com/vi/rOqvZv6lBPw/maxresdefault.jpg",
        "url": "https://www.youtube.com/watch?v=-chpgaUD1lQ"
    },
    {
        "title": "Jani me Fasule",
        "description": "Jani me Fasule është një pjatë e thjeshtë dhe e shijshme e përgatitur me fasule të ziera dhe miell misri.",
        "image": "https://www.plantbasedredhead.com/wp-content/uploads/2021/01/Jani-me-Fasule_Albanian-white-bean-soup_Albanische-weise-Bohnensuppe-_plantbasedredhead.com_1.jpg",
        "url": "https://www.albanianrecipes.com/jani-me-fasule-recipe/"
    },
    {
        "title": "Tavë Elbasani",
        "description": "Tavë Elbasani është një pjatë tradicionale që kombinon mishin e pjekur me oriz dhe domate.",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6gyOlzoluYmNj6yvKUYEkEnd5Rr66PBUnXVqYouK6Jg&s",
        "url": "https://www.youtube.com/watch?v=yoGmowLn3dM"
    },
    {
        "title": "Kos me Arra",
        "description": "Kos me Arra është një ëmbëlsirë tradicionale që përfshin kosin e bërë me mjaltë dhe arra të grira.",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBwv0CuSgFJrzs7oJleF9x727ezbqCpb0IBU2HSKbueQ&s",
        "url": "https://www.youtube.com/watch?v=I0qMaFvfv_0"
    },
    {
        "title": "Pite me Spinaq",
        "description": "Pite me Spinaq është një pjatë e shijshme e përgatitur me spinaq të skuqur dhe miell te pergatitur mire .",
        "image": "https://www.pergatit.com/wp-content/uploads/2016/09/Screenshot_7.png",
        "url": "https://www.youtube.com/watch?v=Ub3t2ec5Fao"
    },
    {
        "title": "Tavë Dheu me Perime",
        "description": "Tavë Dheu me Perime është një pjatë tradicionale që kombinon mishin e pjekur me perime të ndryshme.",
        "image": "https://i.ytimg.com/vi/eUeBi_kZ5lo/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLDUspsE_eI5mHIhc8v4Tab6Po5Ssg",
        "url": "https://www.youtube.com/watch?v=RpG7rmxEdoU"
    },
    {
        "title": "Speca të Mbushur me Oriz dhe Djathë",
        "description": "Speca të Mbushur me Oriz dhe Djathë janë një pjatë  e shëndetshme e përgatitur me speca të mbushur me oriz dhe djathë.",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTSlyfVcKeMTKTLPZugIghPVaU81VzqVcHM9N4IgVFFjA&s",
        "url": "https://www.youtube.com/watch?v=aZ5Wh7da6fE"
    },
    {
        "title": "Pule me Oriz dhe Patate",
        "description": "Pule me Oriz dhe Patate është një pjatë e shijshme dhe e thjeshtë e përgatitur me pule të pjekur, oriz dhe patate.",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQShjyZ9OmFYcQgp0SYyApi_U9CwQelLKSWnzsSRJLY1A&s",
        "url": "https://www.youtube.com/watch?v=dd_UToEPlyo"
    },
    {
        "title": "Pita",
        "description": "Pita është një pjatë e zakonshme shqiptare e përgatitur me mish të pjekur, oriz dhe perime.",
        "image": "https://assets.unileversolutions.com/recipes-v2/216403.jpg",
        "url": "https://www.youtube.com/watch?v=NPiA69p4gqE"
    },
    {
        "title": "Petulla",
        "description": "Petulla është një ëmbëlsirë tradicionale shqiptare e përgatitur me miell, kos dhe sheqer.",
        "image": "https://i.pinimg.com/736x/38/ce/13/38ce13a63070f455917b041465207ca3.jpg",
        "url": "https://www.youtube.com/watch?v=l9TnYeyg6Os"
    },
    {
    "title": "Qifqi",
    "description": "Qifqi është një pjatë tradicionale shqiptare e përgatitur me oriz të skuqur, vezë dhe djathë.",
    "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRxq6FIlyrpiVcHXPVREkjyC-sc0gI6-gIcijthH2yLIA&s",
    "url": "https://www.youtube.com/watch?v=LePC99JPbNQ"
}


]


@app.route('/recipes/sugjerime')
def sugjerime():
    return render_template('sugjerime.html', recipes=recipes)

@app.route('/search')
def search():
    query = request.args.get('query')
    if query:
        # Filter recipes based on the search query
        filtered_recipes = [recipe for recipe in recipes if query.lower() in recipe['title'].lower()]
        return render_template('sugjerime.html', recipes=filtered_recipes)
    else:
        # If no query is provided, show all recipes
        return render_template('sugjerime.html', recipes=recipes)

