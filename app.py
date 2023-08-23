"""Blogly application."""

from flask import Flask, render_template, request, redirect
from models import db, connect_db, User, Post

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "123"

connect_db(app)

@app.route('/')
def home():
    # users = User.query.all()
    # user1 = User(first_name = "Luis", last_name = "Hernandez")
    # db.session.add(user1)
    # db.session.commit()
    return redirect('/users')

@app.route('/users')
def users():
    users = User.query.all()
    posts = Post.query.all()
    return render_template('home.html', users=users, posts=posts)

@app.route('/users/<int:user_id>')
def show_user_detail(user_id):
    user = User.query.get(user_id)
    posts = user.posts
    return render_template('details.html', user=user, posts = posts)

@app.route('/users/new')
def show_new_user_form():
    return render_template('new-user.html')

@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Show detailed post information"""
    post = Post.query.get(post_id)
    return render_template('post-details.html', post=post)

#-------------POSTS, EDITS,DELETES-------------

@app.route('/users/new', methods=['POST'])
def handle_new_user_form():
    id = request.form.get('id')
    id = id if id else None
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    image_url = request.form.get('image_url')
    image_url = image_url if image_url else None

    if id is not None:
        new_user = User(id = id, first_name = first_name, last_name = last_name, image_url = image_url) 
        db.session.add(new_user)
        db.session.commit()
    else:
        new_user = User( first_name = first_name, last_name = last_name, image_url = image_url) 
        db.session.add(new_user)
        db.session.commit() 
    
    return redirect(f'/users/{new_user.id}')

@app.route('/users/<int:user_id>/edit')
def show_user_edit(user_id):
    user = User.query.get(user_id)
    return render_template('edit.html', user=user)
    
@app.route('/users/<int:user_id>/edit', methods=['POST'])
def handle_user_edit(user_id):
    user = User.query.get(user_id)
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    img_url  = request.form.get('img_url')
    img_url = img_url if img_url else None
    user.update_user(first_name,last_name,img_url)
    return redirect(f'/users/{user_id}')

@app.route('/users/<int:user_id>/delete')
def delete_user(user_id):
    user = User.query.get(user_id)
    user.delete_user()
    return redirect('/users')

@app.route('/posts/<int:post_id>/edit')
def show_edit_post(post_id):
    post = Post.query.get(post_id)
    return render_template('post-edit.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def handle_post_edit(post_id):
    post = Post.query.get(post_id)
    title = request.form.get('title')
    content = request.form.get('content')
    post.update_post(title = title, content = content)
    return redirect(f'/posts/{post.id}')
    
@app.route('/posts/<int:post_id>/delete')
def delete_post(post_id):
    post = Post.query.get(post_id)
    user_id = post.user_id
    post.delete_post()
    return redirect(f'/users/{user_id}')

@app.route('/users/<int:user_id>/posts/new')
def show_new_post_form(user_id):
    user = User.query.get(user_id)
    return render_template('new-post.html', user = user)

@app.route('/users/<int:user_id>/posts/new', methods = ['POST'])
def handle_new_post(user_id):
    user = User.query.get(user_id)
    title= request.form.get('title')
    content= request.form.get('post-content')
    user.new_post(title=title, content=content, user_id = user.id)
    return redirect(f'/users/{user.id}')