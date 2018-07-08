from flask import Blueprint
from flask import render_template

blog = Blueprint('blog', __name__, template_folder='./templates')


@blog.route('/')
def index():
    return render_template('index.html')
