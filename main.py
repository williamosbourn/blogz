from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


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

@app.route('/', methods=['POST', 'GET'])
def index():
    blog_list = Blog.query.all()
    return render_template('blog.html',title="Build A Blog", bloglist=blog_list)



if __name__ == '__main__':
    app.run()