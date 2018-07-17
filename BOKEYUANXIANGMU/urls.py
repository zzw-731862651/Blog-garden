"""BOKEYUANXIANGMU URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from cmdb import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index,name='index'),
    path('', views.index,name='index'),
    path('digg/', views.digg,),
    path('code/', views.code),
    path('comment/', views.comment),
    path('backend/', views.backend),
    path('backend/add_article/', views.add_article),
    path('upload/', views.upload),
    path('login/', views.login,name='login'),
    path('logout/', views.logout,name='logout'),

    re_path('(?P<username>\w+)/articles/(?P<article_id>\d+)', views.article_detail,),
    # 点击标签和分类进行自动跳转
    re_path('(?P<username>\w+)/(?P<condition>category|tag|achrive)/(?P<params>.*)', views.homesite),
    re_path('delete/(?P<id>\d+)', views.delete),
    re_path('edit/(?P<id>\d+)', views.edit),

    #走入个人站点
    re_path('(?P<username>\w+)/$', views.homesite,name='homesite'),


]
