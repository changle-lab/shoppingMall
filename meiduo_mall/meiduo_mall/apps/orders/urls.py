from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^orders/settlement/$', views.OrdersView.as_view()),
    url(r'^orders/$', views.SaveOrderView.as_view()),
]