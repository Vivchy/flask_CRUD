from flask import Blueprint, render_template



show_posts = Blueprint('show_posts', __name__, template_folder='templates', static_folder='static')


@show_posts.route('/')
def index():

    return render_template('show_posts/index.html')
