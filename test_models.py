from unittest import TestCase

from app import app
from models import db, User

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = True

app.config['TESTING'] = True

db.drop_all()
db.create_all()

class UserTestCase(TestCase):
    """Test for model User"""
    
    def setUp(self):
        """clean up any existing users"""
        
        User.query.delete()
        
    def teardown(self):
        db.session.rollback()
        
    def test_full_name(self):
        """Test full name variants for property(fget,fset,fdel)"""
        user1 = User(first_name = "Luis", last_name = "Hernandez")
        self.assertEquals(user1.full_name, "Luis Hernandez")
        self.assertEquals(user1._update_user_full_name("Miguel Hernandez"), "Miguel Hernandez")
        
    def test_update_user(self):
        """Test update_user functionality"""
        user1 = User(first_name = "Luis", last_name = "Hernandez")
        db.session.add(user1)
        db.session.commit()
        self.assertAlmostEquals(user1.update_user(first_name= "Miguel", last_name= "Hernandez", img= None), "Miguel Hernandez")
        
        
    def test_delete_user(self):
        """Test delete_user functionality"""
        user1 = User(first_name = "Luis", last_name = "Hernandez")
        db.session.add(user1)
        db.session.commit()
        user1.delete_user()
        self.assertIsNone(User.query.get(user1.id))