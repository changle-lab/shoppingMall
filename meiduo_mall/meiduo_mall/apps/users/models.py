from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False)

    class Meta:
        # 指定模型类的名字
        db_table = "tb_users"
        #模型类在admin中显示的名子
        verbose_name = "用户"
        #复数形式显示什么名字
        verbose_name_plural = verbose_name