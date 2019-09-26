from django.conf.urls import url
from . import views

urlpatterns = [
        url(r'^qq/authorization/$', views.QQLoginUrlView.as_view()),
        url(r'^qq/user/$', views.QQAuthUserView.as_view()),


]