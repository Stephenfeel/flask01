from flask import current_app
from qiniu import Auth,put_data
# 表示接收的浏览器传递的文件对象
def upload_pic(f1):
    access_key = current_app.config.get('QINIU_AK')
    secret_key = current_app.config.get('QINIU_SK')
    # 空间名称
    bucket_name = current_app.config.get('QINIU_BUCKET')
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # ⽣成上传 Token
    token = q.upload_token(bucket_name)
    # 上传⽂件数据，ret是字典，键为hash、key，值为新⽂件名，info是response对象
    ret, info = put_data(token, None, f1.read())
    return ret.get('key')