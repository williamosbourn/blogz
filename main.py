from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)  

    def __init__(self, title, body):
        self.title = title
        self.body = body


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
            new_post = Blog(blog_title, blog_entry)
            db.session.add(new_post)
            db.session.commit()
            return render_template('blog.html', blog_title=blog_title, blog_entry=blog_entry)
    else:
        title_error = ''
        entry_error = ''
        
    return render_template('newpost.html', title="Add a Blog Entry", title_error=title_error, entry_error=entry_error)


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('blog.html',title="Build A Blog")



if __name__ == '__main__':
    app.run()