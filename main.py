from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)  
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.pw_hash = make_pw_hash(password) 
    
    def __repr__(self):
        return '<User %r>' % self.email



def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present



@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        blog_title = request.form['blog_name']
        blog_entry = request.form['blog_entry']
        title_error = ''
        entry_error = ''
   
        if (not blog_title) or (blog_title.strip()==''):
            title_error = 'Please fill in the title'
        
        if (not blog_entry) or (blog_entry.strip()==''):
            entry_error = 'Please fill in the blog entry'
        
        if not title_error and not entry_error:
            new_post = Blog(blog_title, blog_entry, logged_in_user()) 
            db.session.add(new_post)
            db.session.commit()

            blog_id = Blog.query.order_by(Blog.id.desc()).first().id
            return redirect('/postblog?id={}'.format(blog_id))
    else:
        title_error = ''
        entry_error = ''
        
    return render_template('newpost.html', title="Add a Blog Entry", title_error=title_error, entry_error=entry_error)

@app.route('/postblog')
def postblog():
    blog_id = request.args.get('id')  
    post= Blog.query.filter_by(id=blog_id).first() 

    return render_template('postblog.html', post=post)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(email):
            flash('OH NO! "' + email + '" does not seem like an email address')
            return redirect('/signup')
        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('yikes! "' + email + '" is already taken and password reminders are not implemented')
            return redirect('/signup')
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['email'] = user.email
        return redirect("/newpost")
    else:
        return render_template('signup.html')

@app.route("/logout", methods=['POST'])
def logout():
    del session['email']
    return redirect("/")



@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['email'] = user.email
            flash('welcome back, '+user.email)
            return redirect("/newpost")
        flash('bad username or password')
        return redirect("/login")



def logged_in_user():
    owner = User.query.filter_by(email=session['email']).first()
    return owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        # return request.endpoint

        return redirect('/login')



# @app.route('/index')





@app.route('/index', methods=['POST', 'GET'])
def index():
    blog_list = Blog.query.all()
    return render_template('blog.html',title="Build A Blog", bloglist=blog_list)



if __name__ == '__main__':
    app.run()