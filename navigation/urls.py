from django.urls import path

from . import views

app_name = 'navigation'
urlpatterns = [
    path('', views.index, name='index'),
    path('soup', views.soup, name='soup'),
    path('list', views.list, name='list'),
    path('update', views.update, name='update')
]
