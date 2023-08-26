"""Blogly application."""

from flask import Flask, render_template, request, redirect
from models import db, connect_db, User, Post, Tag, PostTag, de_structure_loops, solve_ids_to_remove

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
    return render_template('details.html', user=user, posts=posts)


@app.route('/users/new')
def show_new_user_form():
    return render_template('new-user.html')


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Show detailed post information"""
    post = Post.query.get(post_id)
    tags = post.tags
    return render_template('post-details.html', post=post, tags=tags)

# -------------POSTS, EDITS,DELETES----USERS and POSTS-------------


@app.route('/users/new', methods=['POST'])
def handle_new_user_form():
    id = request.form.get('id')
    id = id if id else None
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    image_url = request.form.get('image_url')
    image_url = image_url if image_url else None

    if id is not None:
        new_user = User(id=id, first_name=first_name,
                        last_name=last_name, image_url=image_url)
        db.session.add(new_user)
        db.session.commit()
    else:
        new_user = User(first_name=first_name,
                        last_name=last_name, image_url=image_url)
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
    img_url = request.form.get('img_url')
    img_url = img_url if img_url else None
    user.update_user(first_name, last_name, img_url)
    return redirect(f'/users/{user_id}')


@app.route('/users/<int:user_id>/delete')
def delete_user(user_id):
    user = User.query.get(user_id)
    user.delete_user()
    return redirect('/users')


@app.route('/posts/<int:post_id>/edit')
def show_edit_post(post_id):
    post = Post.query.get(post_id)
    own_tags = post.tags
    tags = db.session.query(Tag).all()
    return render_template('post-edit.html', post=post, own_tags=own_tags, tags=tags)


@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def handle_post_edit(post_id):
    post = Post.query.get(post_id)
    title = request.form.get('title')
    content = request.form.get('content')

    tag_delete = request.form.getlist('!tag')
    tag_delete = map(int, tag_delete)

    tag_ids = request.form.getlist('tag')
    tag_ids = map(int, tag_ids)

    ids_to_remove = solve_ids_to_remove(tag_delete, tag_ids)

    post = post.update_post(title=title, content=content,
                            tag_ids=tag_ids, ids_to_remove=ids_to_remove)

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
    tags = db.session.query(Tag).all()
    return render_template('new-post.html', user=user, tags=tags)


@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def handle_new_post(user_id):
    user = User.query.get(user_id)
    title = request.form.get('title')
    content = request.form.get('post-content')
    tags = request.form.getlist('tag')
    tags = map(int, tags)
    tags = list(tags)

    user = user.new_post(title=title, content=content,
                         user_id=user.id, tags=tags)
    return redirect(f'/users/{user.id}')

# ---------------------TAGS--------------------


@app.route('/tags')
def show_tags():
    tags = db.session.query(Tag).all()
    return render_template('tags.html', tags=tags)


@app.route('/tags/<int:tag_id>')
def show_tag_details(tag_id):
    tag = db.session.query(Tag).filter(Tag.id == tag_id).first()
    posts = tag.posts
    return render_template('tag-details.html', tag=tag, posts=posts)


@app.route('/tags/new')
def show_tag_form():
    posts = db.session.query(Post).all()
    return render_template('new-tag.html', posts=posts)


@app.route('/tags/new', methods=['POST'])
def handle_new_tags():
    tag_name = request.form.get('name_tag')
    tag_name = tag_name if tag_name else None
    new_tag = Tag(name=tag_name)

    post_ids = request.form.getlist('post')
    post_ids = map(int, post_ids)

    new_tag.handle_tag(tag_name, post_ids, None)
    return redirect(f'/tags/{new_tag.id}')


@app.route('/tags/<int:tag_id>/edit')
def show_edit_tag_form(tag_id):
    tag = db.session.query(Tag).filter(Tag.id == tag_id).first()
    tag_posts = tag.posts
    posts = db.session.query(Post).all()

    common_posts = de_structure_loops(posts, tag_posts)
    return render_template('tag-edit.html', tag=tag, posts=posts, common_posts=common_posts)


@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def handle_tag_edit(tag_id):
    tag = db.session.query(Tag).filter(Tag.id == tag_id).first()
    name = request.form.get('name_tag')
    name = name if name else None
    post_ids = request.form.getlist('post')
    # post_ids = map(int, post_ids)

    post_delete = request.form.getlist('!post')
    # post_delete = map(int, post_delete)

    ids_to_remove = solve_ids_to_remove(post_delete, post_ids)

    # assert ids_to_remove == 10, ids_to_remove

    tag = tag.handle_tag(name, post_ids, ids_to_remove)
    return redirect(f'/tags/{tag.id}')
