from django.conf.urls import url
from . import views
from rest_framework.routers import DefaultRouter


urlpatterns = [
    url(r'^categories/(?P<pk>\d+)/$', views.CategoriesView.as_view()),
    url(r'^categories/(?P<pk>\d+)/skus/$', views.SKUSView.as_view()),
    url(r'^browse_histories/$', views.SKUHistoryView.as_view()),

]

router = DefaultRouter()
router.register('skus/search', views.SKUSearchView, base_name='skus_search')

urlpatterns += router.urls