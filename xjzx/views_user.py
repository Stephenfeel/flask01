from datetime import datetime
import functools
from flask import Blueprint, make_response, session, jsonify
from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from models import db,UserInfo, NewsInfo, NewsCategory
from utils.qiniu_xjzx import upload_pic

user_Blueprint = Blueprint('user', __name__, url_prefix='/user')


@user_Blueprint.route('/image_yzm')
def image_yzm():
    from utils.captcha.captcha import captcha
    # name表示一个随机的名称
    name, yzm, buffer = captcha.generate_captcha()

    # 讲验证码存入session中，可用于后续请求时候对比
    session['image_yzm'] = yzm

    # make_response()函数用来构造一个Response对象，第一个参数为响应的正文
    response = make_response(buffer)
    response.mimetype = 'image/png'

    return response


@user_Blueprint.route('/sms_yzm')
def sms_yzm():
    # 获取手机号，图片验证码
    dict1 = request.args
    mobile = dict1.get('mobile')
    image_yzm = dict1.get('image_yzm')

    if image_yzm.upper() != session['image_yzm'].upper():
        return jsonify(data=1)

    # 判断手机号是否存在


    from utils.ytx_sdk import ytx_send
    import random
    yzm = random.randint(1000, 9999)
    session['sms_yzm'] = yzm
    # 记得填测试号
    ytx_send.sendTemplateSMS(mobile, {yzm, 1}, 1)

    print(yzm)
    return jsonify(data=2)


@user_Blueprint.route('/regsiter', methods=['POST'])
def register():
    dict1 = request.form
    mobile = dict1.get('mobile')
    image_yzm = dict1.get('image_yzm')
    sms_yzm = dict1.get('sms_yzm')
    pwd = dict1.get('pwd')

    # all()接收整个列表，逐个判断是否为空,如果有一个为空，就返回False
    if not all([mobile, image_yzm, sms_yzm, pwd]):
        return jsonify(result=1)

    if image_yzm != session['image_yzm']:
        return jsonify(result=2)

    if int(sms_yzm) != session['sms_yzm']:
        return jsonify(result=3)

    import re
    if not re.match(r'[0-9A-Za-z]{6,20}', pwd):
        return jsonify(result=4)


    mobile_count = UserInfo.query.filter_by(mobile=mobile).count()

    if mobile_count > 0:
        return jsonify(result=5)

    user = UserInfo()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = pwd

    try:
        db.session.add(user)
        db.session.commit()
    except:
        current_app.logger_xjzx.error('注册用户时数据库访问出错')
        return jsonify(result=6)

    return jsonify(result=7)

@user_Blueprint.route('/login',methods=['POST'])
def login():
    dict1=request.form
    mobile = dict1.get('mobile')
    pwd = dict1.get('pwd')

    if not all([mobile,pwd]):
        return jsonify(result=1)

    user=UserInfo.query.filter_by(mobile=mobile).first()
    if user:
        if user.check_pwd(pwd):
            session['user_id']=user.id
            return jsonify(result=3,avatar=user.avatar,nick_name=user.nick_name)
        else:
            return jsonify(result=4)
    else:
        return jsonify(result=2)

@user_Blueprint.route('/logout',methods=['POST'])
def logout():
    session.pop('user_id')
    return jsonify(result=1)


def login_require(fun1):
    @functools.wraps(fun1) #返回fun1函数的名称，而不是用fun1代替函数的名称
    def call_in(*args,**kwargs):
        if 'user_id' not in session:
            return redirect('/')
        return fun1(*args,**kwargs)

    return call_in


@user_Blueprint.route('/')
@login_require
def index():
    user_id=session['user_id']
    user=UserInfo.query.get(user_id)
    return render_template('news/user.html',user=user,title='用户中心')

@user_Blueprint.route('/base',methods=['GET','POST'])
@login_require
def base():
    user_id=session['user_id']
    user=UserInfo.query.get(user_id)

    if request.method=='GET':
        return render_template('news/user_base_info.html',user=user)

    elif request.method=='POST':
        dict1=request.form
        print(dict1, '修改成功')
        signature = dict1.get('signature')
        nick_name = dict1.get('nick_name')
        gender = dict1.get('gender')

        user.signature=signature
        user.nick_name=nick_name
        user.gender = True if gender=='True' else False

        try:
            db.session.commit()
        except Exception as e:
            print(e)
            current_app.logger_xjzx.error('修改用户信息时数据库出错')
            return jsonify(result=2)

        return jsonify(result=1)

@user_Blueprint.route('/pic',methods=['GET','POST'])
@login_require
def pic():
    user_id=session['user_id']
    user=UserInfo.query.get(user_id)

    if request.method=='GET':
        return render_template('news/user_pic_info.html',user=user)

    elif request.method=='POST':
        f1=request.files.get('avatar')
        from utils.qiniu_xjzx import upload_pic

        f1_name=upload_pic(f1)
        user.avatar=f1_name

        db.session.commit()
        return jsonify(result=1,avatar_url=user.avatar_url)


@user_Blueprint.route('/follow')
@login_require
def follow():
    user_id=session['user_id']
    user=UserInfo.query.get(user_id)
    page=int(request.args.get('page',1))

    pagination=user.follow_user.paginate(page,4,False)
    user_list=pagination.items
    total_page=pagination.pages

    return render_template('news/user_follow.html'
                           ,user_list=user_list
                         ,total_page=total_page,
                           page=page
                           )

@user_Blueprint.route('/pwd',methods=['GET','POST'])
@login_require
def pwd():
    if request.method=='GET':
        return render_template('news/user_pass_info.html')
    elif request.method=='POST':
        # 接收用户填写的数据，进行密码修改
        msg = '修改成功'
        # 1.接收数据
        dict1 = request.form
        current_pwd = dict1.get('current_pwd')
        new_pwd = dict1.get('new_pwd')
        new_pwd2 = dict1.get('new_pwd2')
        # 2.进行验证
        # 2.0验证数据是否存在
        if not all([current_pwd, new_pwd, new_pwd2]):
            return render_template(
                'news/user_pass_info.html',
                msg='密码都不能为空'
            )
        # 2.1验证密码格式
        import re
        if not re.match(r'[a-zA-Z0-9_]{6,20}', current_pwd):
            return render_template(
                'news/user_pass_info.html',
                msg='当前密码错误'
            )
        if not re.match(r'[a-zA-Z0-9_]{6,20}', new_pwd):
            return render_template(
                'news/user_pass_info.html',
                msg='新密码格式错误（长度为6-20，内容为大小写a-z字母，0-9数字，下划线_）'
            )
        # 2.2两个密码是否一致
        if new_pwd != new_pwd2:
            return render_template(
                'news/user_pass_info.html',
                msg='两个新密码不一致'
            )

        # 2.3旧密码是否正确
        user_id = session['user_id']
        user = UserInfo.query.get(user_id)
        if not user.check_pwd(current_pwd):
            return render_template(
                'news/user_pass_info.html',
                msg='当前密码错误'
            )

        # 3.修改
        user.password = new_pwd
        # 4.提交到数据库
        db.session.commit()
        # 5.响应
        return render_template(
            'news/user_pass_info.html',
            msg='密码修改成功'
        )

@user_Blueprint.route('/collect')
@login_require
def collection():
    user_id=session['user_id']
    user=UserInfo.query.get(user_id)

    page=int(request.args.get('page',1))
    pagenation=user.news_collect.order_by(NewsInfo.id.desc()).paginate(page,3,False)

    newlist=pagenation.items
    total_page=pagenation.pages

    return render_template('news/user_collection.html'
                           ,newlist=newlist,
                           total_page=total_page,
                           page=page
                           )

@user_Blueprint.route('/release',methods=['GET','POST'])
@login_require
def release():
    category_list = NewsCategory.query.all()
    news_id = request.args.get('news_id')
    print(news_id)
    if request.method=='GET':
        if news_id is None:
            return render_template('news/user_news_release.html',category_list=category_list,news=None)
        else:
            news = NewsInfo.query.get(int(news_id))
            return render_template('news/user_news_release.html',
                                   category_list=category_list
                                   ,news=news
                                   )

    elif request.method=='POST':
        dict1=request.form
        title=dict1.get('title')
        category_id=dict1.get('category')
        summary=dict1.get('summary')
        content=dict1.get('content')

        news_pic=request.files.get('news_pic')

        if news_id is None:
            if not all([title,category_id,summary,content,news_pic]):
                return render_template('news/user_news_release.html',msg='请将信息填写完整')
        else:
            if not all([title,category_id,summary,content]):
                return render_template('news/user_news_release.html',msg='请将信息填写完整')

        if news_pic:
            filename=upload_pic(news_pic)

        if news_id is None:
            news=NewsInfo()
        else:
            news=NewsInfo.query.get(news_id)

        if news_pic:
            news.pic=filename
        news.title=title
        news.category_id=int(category_id)
        news.summary=summary
        news.content=content
        news.status=1
        news.update_time=datetime.now()
        news.user_id=session['user_id']

        db.session.add(news)
        db.session.commit()

        return redirect('/user/newlist')

@user_Blueprint.route('/newlist')
@login_require
def newlist():
    user_id=session['user_id']
    user=UserInfo.query.get(user_id)

    page=int(request.args.get('page','1'))
    pagination=user.news.order_by(NewsInfo.update_time.desc()).paginate(page,6,False)
    total_page=pagination.pages
    news_list=pagination.items


    return render_template('news/user_news_list.html',
                           news_list=news_list,
                           total_page=total_page,
                           page=page
                           )
