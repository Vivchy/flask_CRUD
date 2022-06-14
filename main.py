from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a really really really really long secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


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
    eng_word = '1234567890qwertyuiopasdfghjklzxcvbnm'
    for w in text:
        word = w.lower()
        if word in word_translate.keys():
            slug += word_translate[word]
        elif word in eng_word:
            slug += word
    return slug


class ContactForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()], render_kw={"placeholder": "имя", "class":"new"})
    email = StringField("Email: ", validators=[Email()], default='mail@mail.com')
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/contact', methods=['get', 'post'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        print(name)
        print(email)
        print(message)
        # здесь логика базы данных
        print("\nData received. Now redirecting ...")
        return redirect(url_for('contact'))
    form.name(class_="text_blob")
    return render_template('contact.html', form=form)


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


post_tags = db.Table('post_tags',
                     db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
                     )


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


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    posts = db.relationship('Post', secondary=post_tags, backref='tags')

    def __repr__(self):
        return self.name


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@app.route('/')
def index():
    return render_template('index.html', menu=menu())


@app.route('/create', methods=['POST', 'GET'])
def create():
    tag = db.session.query(Tag).all()

    arr_tag = []
    if request.method == 'POST':
        print(request.form)
        try:
            arr = request.form.getlist('arr')

            title = request.form['title']
            slug = slug_translator(title)
            content = request.form['content']
            p = Post(title=title, slug=slug, content=content)

            db.session.add(p)
            for r in arr:
                the_tag = Tag.query.get(r)
                the_tag.posts.append(p)
                db.session.add(the_tag)
            db.session.commit()

            return render_template('create.html', add_post='запись добавлена', menu=menu(), tag=tag, arr_tag=arr_tag)
        except Exception as e:
            print(e)
    return render_template('create.html', menu=menu(), tag=tag, arr_tag=arr_tag)


@app.route('/posts')
def posts():
    posts = db.session.query(Post).all()
    imp = db.session.query(Important).all()
    result = {}
    print(imp[1].posts)

    return render_template('posts.html', posts=posts, imp=imp, menu=menu())


@app.route('/delete/<int:id>')
def delete(id):
    delete_post = db.session.query(Post).get(id)
    db.session.delete(delete_post)
    db.session.commit()
    return redirect(url_for('posts'))


@app.route('/post/<slug>')
def post(slug):
    post = db.session.query(Post).filter(Post.slug == slug).first()
    important = db.session.query(Important).get(post.important_id)
    return render_template('post.html', post=post, imp=important, menu=menu())


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
        return redirect(url_for('post', slug=post.slug))
    return render_template('update.html', post=post, menu=menu())


@app.route('/admin/')
@login_required
def admin():
    return render_template('admin.html', menu=menu())


@app.route('/login/', methods=['post', 'get'])
def login():
    message = ''
    if request.method == 'POST':
        print(request.form)
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'root' and password == 'pass':
            message = "Correct username and password"
        else:
            message = "Wrong username or password"

    return render_template('login.html', message=message, menu=menu())


if __name__ == "__main__":
    app.run(debug=True)
