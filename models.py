"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    app.app_context().push()
    db.init_app(app)


class User(db.Model):
    __tablename__ = 'users'

    """User model"""
    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    first_name = db.Column(db.String(20),
                           nullable=False)
    last_name = db.Column(db.String(20),
                          nullable=True)
    image_url = db.Column(db.String,
                          nullable=True,
                          default="https://w7.pngwing.com/pngs/178/595/png-transparent-user-profile-computer-icons-login-user-avatars-thumbnail.png")

    # can also use @property and later @full_name.setter/getter/deleter

    def _get_user_full_name(self):
        first = self.first_name
        last = self.last_name
        return first + ' ' + last

    def _update_user_full_name(self, name):
        """"splits the name value into substrings to respectively first and last names and"""
        splitted = name.split()
        if len(splitted) <= 2:
            first_name = splitted[0]
            last_name = splitted[1]
            self.first_name = first_name
            self.last_name = last_name
            db.session.add(self)
            db.session.commit()
        elif len(splitted) == 1:
            first_name = splitted[0]
            db.session.add(first_name)
            db.session.commit()
        return self.full_name

    def _delete_user_full_name(self):
        userx = User.query.filter(User.id == self.id).delete()
        print(userx)

    full_name = property(
        fget=_get_user_full_name,
        fset=_update_user_full_name,
        fdel=_delete_user_full_name
    )

    def update_user(self, first_name, last_name, img):
        user = User.query.get(self.id)
        if img is None:
            user.first_name = first_name
            user.last_name = last_name

            db.session.add(user)
            db.session.commit()
        elif img is not None:
            user.first_name = first_name
            user.last_name = last_name
            user.image_url = img
            db.session.add(user)
            db.session.commit()
        else:
            raise Exception('User not found')
        return user.full_name

    def delete_user(self):
        user = User.query.get(self.id)
        db.session.delete(user)
        db.session.commit()

    def new_post(self, title, content, user_id, tags):
        post = Post(title=title, content=content, user_id=user_id)
        for tag in tags:
            unique_tag = db.session.query(Tag).filter(Tag.id == tag).first()
            post.tags.append(unique_tag)
        db.session.add(post)
        db.session.commit()
        return self


class Post(db.Model):
    """Post model class"""

    __tablename__ = 'posts'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    title = db.Column(db.String,
                      nullable=False,
                      unique=True)
    content = db.Column(db.Text,
                        nullable=False)
    created_at = db.Column(db.TIMESTAMP,
                           default=func.now())
    updated_at = db.Column(db.TIMESTAMP,
                           default=func.now(),
                           onupdate=func.now())

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=True)

    user = db.relationship('User', backref='posts', passive_deletes=True)

    posts_and_tags = db.relationship('PostTag', backref='post')

    def update_post(self, title, content, tag_ids, ids_to_remove):
        for id in tag_ids:
            if db.session.query(Tag).filter(Tag.id == id).first() in self.tags:
                continue
            else:
                self.tags.append(db.session.query(
                    Tag).filter(Tag.id == id).first())

        if not title or not content:
            db.session.rollback()
            raise Exception('No values to be updated')
        else:
            self.title = title
            self.content = content
            if ids_to_remove:
                for id in ids_to_remove:
                    if db.session.query(Tag).filter(Tag.id == id).first() in self.tags:
                        self.tags.remove(db.session.query(
                            Tag).filter(Tag.id == id).first())

            db.session.add(self)
            db.session.commit()
        return self

    def delete_post(self):
        post = Post.query.get(self.id)

        db.session.delete(post)
        db.session.commit()


class Tag(db.Model):

    __tablename__ = 'tags'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String,
                     unique=True)

    posts = db.relationship(
        'Post', secondary='posts_tags', backref='tags')

    posts_and_tags = db.relationship(
        'PostTag', backref='tag')

    def handle_tag(self, name, posts_ids, ids_to_remove):

        if name is not None:
            self.name = name
            for id in posts_ids:
                if db.session.query(Post).filter(Post.id == id).first() in self.posts:
                    continue
                else:
                    self.posts.append(db.session.query(
                        Post).filter(Post.id == id).first())

        if ids_to_remove:
            for id in ids_to_remove:
                if db.session.query(Post).filter(Post.id == id).first() in self.posts:
                    self.posts.remove(db.session.query(
                        Post).filter(Post.id == id).first())

        db.session.add(self)
        db.session.commit()
        return self
    # raise Exception('Tags should not be empty')


class PostTag(db.Model):

    __tablename__ = 'posts_tags'

    post_id = db.Column(db.Integer,
                        db.ForeignKey('posts.id', ondelete='CASCADE'),
                        primary_key=True)
    tag_id = db.Column(db.Integer,
                       db.ForeignKey('tags.id', ondelete='CASCADE'),
                       primary_key=True)


def de_structure_loops(posts, tag_posts):
    common_posts = []
    for own_post in tag_posts:
        if own_post in posts:
            common_posts.append(own_post)
    return common_posts


def solve_ids_to_remove(lst, lst2):
    values = []
    item_remove = []
    print(list)
    # x = loop(lst2)
    # for element in remove:
    # new_remove.append([element.split('/')])
    # for element in x:
    #     item_remove.append(element[-1])

    for id in lst:
        if id not in lst2:
            values.append(id)

    return values


# def loop(lst):
#     remove = []
#     for value in lst:
#         if "no" in str(value):
#             remove.append(str(value))
#     return remove


# def solve_proper(lst):
#     for value in lst:
#         clean = [value for value in lst if isinstance(value, int)]
#         return clean
