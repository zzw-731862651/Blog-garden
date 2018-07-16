from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth
from cmdb.models import Article, UserInfo, Category, Tag,ArticleUpDown,Comment,Article2Tag
from django.db.models import Count, Avg
import json
from django.http import JsonResponse
from django.db.models import F
from django.db import transaction
from BOKEYUANXIANGMU import settings
import os
from bs4 import BeautifulSoup


# Create your views here.

# 用户名：zhao 密码:zhao1234
# 用户名：alex 密码:alex1234
def index(request):
    article_list = Article.objects.all()

    return render(request, 'index.html', {"article_list": article_list})


def login(request):
    if request.method == 'POST':
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        user = auth.authenticate(username=user, password=pwd)
        if user:
            auth.login(request, user)
            return redirect('/index/')

    return render(request, 'login.html')


def get_query_data(username):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    cate_list = Category.objects.filter(blog=blog).annotate(c=Count("article__title")).values_list('title', 'c')
    # print(ret)
    # print(res)
    # 查询当前站点每一个标签的名称以及对应的文章数
    # tag_list = Tag.objects.filter(blog_id = blog.nid).annotate(c=Count("article")).values('title','c')
    tag_list = Tag.objects.filter(blog=blog).annotate(c=Count("article__title")).values_list('title', 'c')
    # print(tag_list)
    # print(tag_lis)
    date_list = Article.objects.filter(user=user).extra(
        select={"y_m_date": "DATE_FORMAT(create_time,'%%Y/%%m')"}).values("y_m_date").annotate(
        c=Count("title")).values_list("y_m_date", "c")


    return {"username":username,"blog":blog,"cate_list":cate_list,"tag_list":tag_list,"date_list":date_list}



def homesite(request, username, **kwargs):
    '''
    主要功能就是：查询！！！！很重要
    :param request:
    :param username:
    :return:
    '''
    # print("kwargs", kwargs)
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'not_fond.html')
    # 查询当前站点对象
    blog = user.blog
    if not kwargs:
        article_list = Article.objects.filter(user__username=username)
    else:
        condition = kwargs.get("condition")
        params = kwargs.get("params")
        if condition == "category":
            article_list = Article.objects.filter(user__username=username).filter(category__title=params)
        elif condition == "tag":
            article_list = Article.objects.filter(user__username=username).filter(tags__title=params)
        else:
            year, month = params.split("/")
            # print('****', year, month)

            article_list = Article.objects.filter(user__username=username).filter(create_time__year=year, create_time__month=month)
            #匹配不到月份，将setting中设置   USE_TZ = False
            # print("article_list", article_list)

    if not article_list:
        return render(request,"not_fond.html")

    # 查询当前点击用户对象的所有文章
    # article_list = Article.objects.filter(user_id=user.nid)
    # 查询当前站点每一个分类的名称以及对应的文章数
    # ret = Category.objects.filter(blog_id = blog.nid).annotate(c=Count("article")).values('title','c')
    cate_list = Category.objects.filter(blog=blog).annotate(c=Count("article__title")).values_list('title', 'c')
    # print(ret)
    # print(res)
    # 查询当前站点每一个标签的名称以及对应的文章数
    # tag_list = Tag.objects.filter(blog_id = blog.nid).annotate(c=Count("article")).values('title','c')
    tag_list = Tag.objects.filter(blog=blog).annotate(c=Count("article__title")).values_list('title', 'c')
    # print(tag_list)
    # print(tag_lis)
    date_list = Article.objects.filter(user=user).extra(
        select={"y_m_date": "DATE_FORMAT(create_time,'%%Y/%%m')"}).values("y_m_date").annotate(
        c=Count("title")).values_list("y_m_date", "c")
    # print(date_list)

    return render(request, 'homesite.html', locals())


def article_detail(request,username,article_id):
    content_text = get_query_data(username)

    article_obj = Article.objects.filter(pk=article_id).first()
    comment_list = Comment.objects.filter(article_id=article_id)
    content_text["article_obj"] = article_obj    #字典的增加，content_text为字典，给字典增加一个键值对
    content_text["comment_list"] = comment_list
    return render(request,'article_detail.html',content_text)



def digg(request):     #点赞函数路径视图
    print(request.POST)
    is_up=json.loads(request.POST.get("is_up"))
    article_id=request.POST.get("article_id")
    user_id=request.user.pk
    response={"state":True,"msg":None}

    obj=ArticleUpDown.objects.filter(user_id=user_id,article_id=article_id).first()
    if obj:
        response["state"]=False
        response["handled"]=obj.is_up
    else:
        with transaction.atomic():
            new_obj=ArticleUpDown.objects.create(user_id=user_id,article_id=article_id,is_up=is_up)
            if is_up:
                Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
            else:
                Article.objects.filter(pk=article_id).update(down_count=F("down_count")+1)


    return JsonResponse(response)



def comment(request):

    # 获取数据
    user_id=request.user.pk
    article_id=request.POST.get("article_id")
    content=request.POST.get("content")
    pid=request.POST.get("pid")
    print(pid)
    # 生成评论对象(事物处理)
    with transaction.atomic():    #事物回滚
        comment=Comment.objects.create(user_id=user_id,article_id=article_id,content=content,parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)

    response={"state":True}
    response["timer"]=comment.create_time.strftime("%Y-%m-%d %X")
    response["content"]=comment.content
    response["user"]=request.user.username

    return JsonResponse(response)



def backend(request):
    user=request.user
    article_list = Article.objects.filter(user=user)

    return render(request,'backend/backend.html',locals()) #新添加的templates里面的文件夹路径



def add_article(request):
    if request.method =='POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        user = request.user
        cate_pk = request.POST.get('cate')
        tags_pk_list = request.POST.getlist('tags')
        # print(tags_pk_list)
        soup = BeautifulSoup(content,"html.parser")   #导入bs4模块
        #对文章的文本内容进行过滤
        for tag in soup.find_all():
            if tag.name in ["script",]:
                tag.decompose()

        desc = soup.text[0:200]

        article_obj = Article.objects.create(title=title,content=str(soup),user=user,category_id = cate_pk,desc=desc)
        for tag_pk in tags_pk_list:
            Article2Tag.objects.create(article_id=article_obj.pk,tag_id=tag_pk)
            # print(tag_pk)


        return redirect("/backend/")

    else:
        blog = request.user.blog
        cate_list = Category.objects.filter(blog=blog)
        tags = Tag.objects.filter(blog=blog)
        return render(request,'backend/add_article.html',locals())   #新添加的templates里面的文件夹路径


def edit(request,id):
    if request.method =='POST':

        title = request.POST.get('title')
        content = request.POST.get('content')
        user = request.user
        cate_pk = request.POST.get('cate')
        tags_pk_list = request.POST.getlist('tags')

        article_obj = Article.objects.filter(nid=id).update(title=title,content=content,user=user,category_id = cate_pk,)

        for tag_pk in tags_pk_list:
            Article2Tag.objects.create(article_id=id,tag_id=tag_pk)



        return redirect("/backend/")

    else:
        obj = Article.objects.filter(nid=id).first()
        blog = request.user.blog
        cate_list = Category.objects.filter(blog=blog)
        tags = Tag.objects.filter(blog=blog)
        list1 = Article2Tag.objects.filter(article_id=id).values_list("tag__title")
        list2 = []
        for i in list1:
            j = i[0]
            list2.append(j)
        # list1 = Tag.objects.all()
        # list2 = []
        # for i in list1:
        #     j= i.title
        #     list2.append(j)
        # print(list2)

        return render(request,'backend/edit.html',locals())   #新添加的templates里面的文件夹路径


    # return HttpResponse("ok")


def delete(request,id):

    Article.objects.filter(nid = id).delete()

    return redirect('/backend/')



def upload(request):

    print(request.FILES)
    obj = request.FILES.get("upload_img")
    name = obj.name

    # path =settings.BASE_DIR                                 # 思路：从这里引入settings路径，找到总项目路径
    path = os.path.join(settings.BASE_DIR,"static","upload",name)#用总项目路径，拼接static路径,upload路径，+name,组成一个新的文件名
    with open(path,"wb")as f:
        for line in obj:
            f.write(line)

    res = {
        "error":0,
        "url":"/static/upload/"+name
    }                                         #将结果用反序列化的方式传入富文本编辑器中

    return HttpResponse(json.dumps(res))







def logout(request):
    auth.logout(request)
    return redirect('/index/')
