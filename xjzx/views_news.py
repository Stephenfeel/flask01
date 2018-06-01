from flask import Blueprint,render_template

# 如果希望用户直接访问代码不要写 url
news_blueprint = Blueprint('news',__name__)

@news_blueprint.route('/')
def index():
    return render_template('news/index.html')