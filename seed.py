from app import app
from models import User, Post, db

db.drop_all()
db.create_all()

u1 = User(first_name = "Luis", last_name = "Hernandez")
u2 = User(first_name = "Miguel", last_name = "Hernandez")
u3 = User(first_name = "Jose", last_name = "Ruiz")
u4 = User(first_name = "Timmy", last_name = "Timmy")
u5 = User(first_name = "Rick", last_name = "Morthy")
users = [u1, u2, u3, u4, u5]

p1 = Post(title = 'Power of backend development', 
          content = 'Welcome to todays post, todays topic is the power of python and backend dev',
          user_id = 1)
p2 = Post(title = 'Power of frontend development', 
          content = 'Welcome to todays post, todays topic is the power of js and frontend dev',
          user_id = 4)
posts = [p1, p2]

db.session.add_all(users)
db.session.add_all(posts)

db.session.commit()