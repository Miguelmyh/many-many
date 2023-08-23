from unittest import TestCase

from app import app
from models import db, User, Post

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = True

app.config['TESTING'] = True


class UserTestCase(TestCase):
    """Tests for user app"""
    
                
    def setUp(self):
        db.drop_all()
        db.create_all()
        
        db.session.rollback()
        
        User.query.delete()
        Post.query.delete()
        
        user = User(id = 1, first_name = "Luis", last_name = "Hernandez")
        db.session.add(user)
        db.session.commit()
        post = Post(title = 'Power of backend development', 
        content = 'Welcome to todays post, todays topic is the power of python and backend dev',
        user_id = 1)
        db.session.add(post)
        db.session.commit()
        

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
            
            user = User.query.all()[0]
            post = Post.query.all()[0]
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(user.full_name, html)
            self.assertNotIn(user.image_url, html)
            self.assertIn(post.title, html)
            
    def test_detail_page(self):
        with app.test_client() as client:
            resp = client.get('/users/1')
            html = resp.get_data(as_text=True)
            
            user = User.query.get(1)
            post = Post.query.get(1)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(user.full_name, html)
            self.assertIn(user.image_url, html)
            self.assertIn(post.title, html)
            
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
                "id": 2,
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
            
    def test_delete_user(self):
        with app.test_client() as client:
            
            resp = client.get('/users/1/delete')
            
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.request.path, '/users/1/delete')
            self.assertEqual(resp.location, '/users')
            
            new_resp = client.get('/users')
            html = new_resp.get_data(as_text=True)
            
            self.assertNotIn('Luis Hernandez', html)
            
            
            
    def test_show_post(self):
        with app.test_client() as client:
            resp = client.get('/posts/1')
            html = resp.get_data(as_text=True)
            
            post = Post.query.get(1)
            
            self.assertIn(post.title, html)
            self.assertIn(post.content, html)
            
    def test_show_edit_post(self):
        with app.test_client() as client:
            resp = client.get('/posts/1/edit')
            html = resp.get_data(as_text=True)
            
            self.assertIn( '<form action="/posts/1/edit" method="POST" id="post-form">',html)
            self.assertIn('<div class="post-div-content">', html)
            
            
    def test_handle_post_edit(self):
        with app.test_client() as client:
            resp = client.post('/posts/1/edit', data = {
                "title" : "Updated Post",
                "content" : "this is a updated post",
                "user_id" : 1
                })
            
            post = Post.query.get(1)
            details_resp = client.get('/posts/1')
            html = details_resp.get_data(as_text=True)
            
            self.assertIn('Updated Post', html)
            self.assertNotIn('Power of backend development', html)
            self.assertEqual(post.title, 'Updated Post')
            
    def test_delete_post(self):
        with app.test_client() as client:
            resp = client.get('/posts/1/delete')
            
            self.assertEqual(resp.status_code, 302)
            
            new_resp = client.get('/users/1')
            html = new_resp.get_data(as_text=True)
            
            self.assertNotIn('Power of backend development', html)
            
            # self.assertNotIn('')
            
    def test_show_new_post_form(self):
        with app.test_client() as client:
            resp = client.get('/users/1/posts/new')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="post-btn edit">Add</button>',html)
            self.assertIn('<label for="title" class="labels label-title">Title</label>',html)
            
    def test_handle_show_new_post(self):
        with app.test_client() as client:
            resp = client.post('/users/1/posts/new', data = {
                    "title" : "new post",
                    "post-content" : "This is the new post content",
                    "user_id" : 1
                })
            
            self.assertEqual(resp.status_code, 302)
            
            new_resp = client.get('/users/1')
            html = new_resp.get_data(as_text=True)
            
            self.assertEqual(new_resp.status_code, 200)
            self.assertIn('new post',html)
            