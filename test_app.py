from unittest import TestCase

from app import app
from models import db, User

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = True

app.config['TESTING'] = True

db.drop_all()
db.create_all()

class UserTestCase(TestCase):
    """Tests for user app"""
    
    def setUp(self):
        User.query.delete()
        
        user = User(first_name = "Luis", last_name = "Hernandez")
        db.session.add(user)
        db.session.commit() 
        
        self.user_id = user.id
        
    def tearDown(self):
        """clean up session errors"""
        db.session.rollback()
        # User.query.delete()
        
    def test_homepage(self):
        """test for redirection to users home page"""
        with app.test_client() as client:
            prev_resp = client.get('/')# redirect status code should be 302 or 308
            resp = client.get('/', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(prev_resp.status_code, 302)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.request.path, '/users')
            
    def test_users(self):
        """Test that list of users appear in the page and not to show img_url"""
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)
            users = User.query.all()
            
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(users[0].full_name, html)
            self.assertNotIn(users[0].image_url, html)
            
    def test_detail_page(self):
        with app.test_client() as client:
            resp = client.get('/users/1')
            html = resp.get_data(as_text=True)
            
            user = User.query.all()[0]
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(user.full_name, html)
            self.assertIn(user.image_url, html)
            
    def test_new_user_form(self):
        """Test to check for the from showing up"""
        with app.test_client() as client:
            resp = client.get('/users/new')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<form action="/users/new" method="POST">\n  <input type="text" placeholder="first name" name="first_name" />\n  <input type="text" placeholder="last name" name="last_name" />\n  <input type="text" placeholder="img-url ex. https://image.jpg" />\n  <button>Submit</button>\n</form>'
                ,html)   
            
    def test_new_user_upload(self):
        """Test upload of new user in db and redirect to details of the same user"""  
        with app.test_client() as client:
            resp = client.post('/users/new', data={
                "first_name": "Miguel",
                "last_name": "Hernandez",
                "image_url": None
            })
            #gets new_user
            new_user = User.query.get(2)
            
            self.assertEqual(resp.status_code, 302)#checks redirect 
            self.assertEqual(resp.location, '/users/2', User.query.all())
            
            new_resp = client.get('/users/2')
            html = new_resp.get_data(as_text=True)
            
            self.assertIn(new_user.full_name, html)
            self.assertIn(new_user.image_url, html)
            self.assertIsNotNone(new_user.image_url)
            self.assertIsNotNone(new_user.full_name)