from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^areas/$', views.GetAreasView.as_view()),  # 获取省信息
    url(r'^areas/(?P<pk>\d+)/$', views.GetAreaView.as_view()),  # 获取市和区的信息
    url(r'^addresses/$', views.AddressView.as_view()),  # 保存地址
    url(r'^addresses/(?P<pk>\d+)/$', views.AddressView.as_view()),  # 保存地址

]
