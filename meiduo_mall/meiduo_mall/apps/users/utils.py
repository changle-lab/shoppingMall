import re

from django.contrib.auth.backends import ModelBackend

#重写jwt返回的结果
#再配置文件中进行设置，让程序调用我重写后的方法
from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        "token": token,
        "username": user.username,
        "user_id": user.id
    }

class UsernameMobileAuthBackend(ModelBackend):
    """
    重写django原有的验证用户方法
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if re.match(r'^1[3-9]\d{9}$', username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)
        except:
            user = None

        #验证密码
        if user is not None and user.check_password(password):
            return user