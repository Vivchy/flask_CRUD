from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a really really really really long secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db'

db = SQLAlchemy(app)

def menu():
    menu = db.session.query(Menu).all()
    return menu

def slug_translator(text):
    slug = ''
    word_translate = {"й": "i", "ц": "c", "у": "u", "к": "k", "е": "e", "н": "n",
                      "г": "g", "ш": "sh", "щ": "shj", "з": "z", "х": "h", "ъ": "j",
                      "ф": "f", "ы": "i", "в": "v", "а": "a", "п": "p", "р": "r", "о": "o",
                      "л": "l", "д": "d", "ж": "j", "э": "e", "я": "ya", "ч": "ch", "с": "s",
                      "м": "m", "и": "i", "т": "t", "ь": "j", "б": "b", "ю": "yu", " ": "_"}
    for w in text:
        word = w.lower()
        if word in word_translate.keys():
            slug += word_translate[word]
    return slug


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    important_id = db.Column(db.Integer(), db.ForeignKey('importants.id'), nullable=True)


    def __repr__(self):
        return self.title[:10]


class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return self.title

class Important(db.Model):
    __tablename__ = 'importants'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    posts = db.relationship('Post', backref='important')

    def __repr__(self):
        return self.title

@app.route('/')
def index():
    return render_template('index.html', menu=menu())


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':

        try:
            title = request.form['title']
            slug = slug_translator(title)
            content = request.form['content']
            p = Post(title=title, slug=slug, content=content)
            db.session.add(p)
            db.session.commit()
            print(p.title)
            return render_template('create.html', add_post='запись добавлена', menu=menu())
        except Exception as e:
            print(e)
    return render_template('create.html', menu=menu())


@app.route('/posts')
def posts():
    posts = db.session.query(Post).all()

    return render_template('posts.html', posts=posts, menu=menu())


@app.route('/delete/<int:id>')
def delete(id):
    delete_post = db.session.query(Post).get(id)
    db.session.delete(delete_post)
    db.session.commit()
    return redirect(url_for('posts'))


@app.route('/post/<id>')
def post(id):
    post = db.session.query(Post).get(id)
    return render_template('post.html', post=post, menu=menu())


@app.route('/update/<id>', methods=['POST', 'GET'])
def update(id):
    post = db.session.query(Post).get(id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['text']
        slug = slug_translator(title)
        post.title = title
        post.slug = slug
        post.content = content
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('post', id=post.id))
    return render_template('update.html', post=post, menu=menu())


if __name__ == "__main__":
    app.run(debug=True)
