from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views
urlpatterns = {
        url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMS_Code_View.as_view()),
        url(r'^usernames/(?P<username>\w+)/count/$', views.UserNameView.as_view()),
        url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileView.as_view()),
        url(r'^users/$', views.UserView.as_view()),

        url(r'^user/$', views.UserShowView.as_view()),

        url(r'^authorizations/$', obtain_jwt_token),
    }

