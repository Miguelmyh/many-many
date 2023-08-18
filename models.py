"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy

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
                          default = "https://w7.pngwing.com/pngs/178/595/png-transparent-user-profile-computer-icons-login-user-avatars-thumbnail.png")
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
    fget= _get_user_full_name,
    fset= _update_user_full_name,
    fdel = _delete_user_full_name
    )
        
    def update_user(self, first_name, last_name,img):
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