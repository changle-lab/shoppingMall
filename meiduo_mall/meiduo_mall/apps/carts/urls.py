from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^cart/$', views.CartsView.as_view()),
    url(r'^cart/selection/$', views.CartSelectionView.as_view())
]