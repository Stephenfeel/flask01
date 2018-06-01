from .CCPRestSDK import REST

# import ConfigParser
# 主帐号
accountSid = '8aaf0708639129c40163a1aa45410c9b';
# 主帐号Token
accountToken = 'de347c71238f4232a74d87365dddecf4';
# 应⽤Id
appId = '8a216da85f5c89b1015f994145a21b0d';
# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com';
# 请求端⼝
serverPort = '8883';
# REST版本号
softVersion = '2013-12-26';


# 发送模板短信
# @param to ⼿机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 '',第一个数为验证码的值，第二个数为保留的时间，单位为分
# @param $tempId 模板Id
def sendTemplateSMS(to, datas, tempId):
    # 初始化REST SDK
    rest = REST(serverIP, serverPort, softVersion)
    rest.setAccount(accountSid, accountToken)
    rest.setAppId(appId)

    result = rest.sendTemplateSMS(to, datas, tempId)
    return result.get('statusCode')
