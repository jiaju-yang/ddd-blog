from flask import Blueprint
from flask import render_template

from ...usecase import articles_by_page, article_by_id

blog = Blueprint('blog', __name__, template_folder='./templates')


@blog.route('/')
def index():
    articles = articles_by_page()
    return render_template('index.html', articles=articles)


@blog.route('/article/<int:id>/')
def article(id):
    article = article_by_id(id)
    return render_template('article.html', article=article)
