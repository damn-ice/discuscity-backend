from . import views
from django.urls import path
from django.contrib.auth import views as auth

appname = 'api'

urlpatterns = [
    path('', views.index, name='index'),
    path('create', views.create, name='create'),
    path('home', views.home, name='home'),
    path('image', views.image, name='image'),
    path('update', views.update, name='update'),
    path('test', views.test, name='test'),
    path('topics', views.topics, name='topics'),
    path('emotion', views.emotion, name='emotion'),
    path('section/<str:name>/', views.section, name='section'),
    path('section/<str:name>/<int:topic_id>/', views.topic, name='topic'),
    path('current', views.current, name='current'),
    path('register', views.registerView, name='register'),
    path('login', views.loginView, name='login'),
    path('logout', views.logoutView, name='logout'),
]
