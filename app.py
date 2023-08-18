"""Blogly application."""

from flask import Flask, render_template, request, redirect
from models import db, connect_db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "123"

connect_db(app)
db.create_all()

@app.route('/')
def home():
    users = User.query.all()
    # user1 = User(first_name = "Luis", last_name = "Hernandez")
    # db.session.add(user1)
    # db.session.commit()
    return redirect('/users')

@app.route('/users')
def users():
    users = User.query.all()
    return render_template('home.html', users=users)

@app.route('/users/<int:user_id>')
def show_user_detail(user_id):
    user = User.query.get(user_id)
    return render_template('details.html', user=user)

@app.route('/users/new')
def show_new_user_form():
    return render_template('new-user.html')
@app.route('/users/new', methods=['POST'])
def handle_new_user_form():
    
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    image_url = request.form.get('image_url')
    image_url = image_url if image_url else None
    
    new_user =User(first_name = first_name, last_name = last_name, image_url = image_url) 
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
    return redirect(f'/users')
    