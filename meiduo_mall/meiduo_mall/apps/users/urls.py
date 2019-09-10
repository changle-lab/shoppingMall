from django.conf.urls import url
from . import views

urlpatterns = {
        url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMS_Code_View.as_view()),
    }