from flask import Blueprint,render_template, jsonify
from flask import request
from flask import session

from models import db,NewsCategory, UserInfo, NewsInfo

# 如果希望用户直接访问代码不要写 url
news_blueprint = Blueprint('news',__name__)

@news_blueprint.route('/')
def index():
    # 查询分类种类
    category_list=NewsCategory.query.all()
    if 'user_id' in session:
        user=UserInfo.query.get(session['user_id'])
    else:
        user=None
    #查询点击量最高的6条新闻
    count_list=NewsInfo.query.order_by(NewsInfo.click_count.desc())[0:6]


    return render_template('news/index.html',
                           category_list=category_list,
                           title='首页',
                           user=user
                           ,count_list=count_list
                           )


@news_blueprint.route('/newslist')
def newslist():
    page=int(request.args.get('page','1'))
    pagination=NewsInfo.query
    category_id=int(request.args.get('category_id',0))
    if category_id:
        pagination=pagination.filter_by(category_id=category_id)
    pagination = pagination.order_by(NewsInfo.update_time.desc()).paginate(page,4,False)

    news_list=pagination.items
    total_page=pagination.pages
    news_list2=[]
    for news in news_list:
        dict1={
            'id':news.id,
            'title':news.title,
            'summary':news.summary,
            'pic_url':news.pic_url,
            'user_avatar':news.user.avatar_url,
            'user_id':news.user.id,
            'user_nick_name':news.user.nick_name,
            'update_time':news.update_time
        }
        news_list2.append(dict1)

    return jsonify(page=page,
                   news_list2=news_list2,
                   total_page=total_page
                   )