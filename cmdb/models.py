from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


#1 用户表
#继承了AbstractUser，添加我们需要的字段，手机号，头像，一对一关系
class UserInfo(AbstractUser):
    nid=models.AutoField(primary_key=True)
    telephone=models.CharField(max_length=11,null=True,unique=True)
    avatar=models.FileField(upload_to="avatars/",default="avatars/default.png")
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    blog=models.OneToOneField(to="Blog",to_field='nid',null=True,on_delete=models.CASCADE)


    #定义__str__方法，直接输出对象名时，打印的是username的值
    def __str__(self):
        return self.username

    # class Meta:
    #     #verbose_name 给模型起一个更可读性的名字
    #     verbose_name = "用户信息"
    #     #verbose_name_plural 模型的复数形式指定
    #     verbose_name_plural = verbose_name

#2 博客表
#创建博客标题 /创建博客主题
class Blog(models.Model):
    nid=models.AutoField(primary_key=True)   #自增
    title=models.CharField(verbose_name='个人博客标题',max_length=64) #博客标题
    site_name = models.CharField(verbose_name='站点名称',max_length=64)
    theme=models.CharField(verbose_name='博客主题',max_length=32)     #博客主题

    def __str__(self):
        return self.title

    # class Mede:
    #     verbose_name="博客"
    #     verbose_name_plural=verbose_name


#3 个人博客分类表
#创建分类标题/外键关联博客，一个博客站点可以有多个分类
#建立 与 博客一对多关系 一个博客里有多个分类
class Category(models.Model):   #个人博客文章分类
    nid=models.AutoField(primary_key=True)
    title=models.CharField(verbose_name='分类标题',max_length=64)
    blog=models.ForeignKey(verbose_name='所属博客',to="Blog",to_field="nid",on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    # class Mede:
    #     verbose_name="文章分类"
    #     verbose_name_plural=verbose_name


#4 标签
#创造标签名/所属博客
##建立与博客一对多关系 一个博客可以标记多个标签
class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称',max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客',to="Blog", to_field="nid",on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    # class Meta:
    #     verbose_name = "标签"
    #     verbose_name_plural = verbose_name


#5 文章
# 创建 文章标题/文章描述/创建时间
#建立与博客分类一对多关系 一个博客分类里有多个文章
#建立与用户一对多关系 一个用户可以写多个文章
#建立多对多关联 文章和标签可以互相有多个
class Article(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50,verbose_name='文章标题')
    desc = models.CharField(max_length=255,verbose_name='文章描述')
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    content = models.TextField()
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    user = models.ForeignKey(verbose_name='作者',to="UserInfo",to_field='nid', on_delete=models.CASCADE)

    category = models.ForeignKey(to="Category", to_field="nid", null=True,on_delete=models.CASCADE)



    tags = models.ManyToManyField(
        to="Tag",
        through="Article2Tag",
        through_fields=("article", "tag"),
    )

    def __str__(self):
        return self.title

    # class Meta:
    #     verbose_name = "文章"
    #     verbose_name_plural = verbose_name


# 6 文章和标签的多对多关系表
class Article2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章',to="Article", to_field="nid",on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name='标签',to="Tag", to_field="nid",on_delete=models.CASCADE)

    # def __str__(self):
    #     return "{}-{}".format(self.article, self.tag)

    # class Meta:
    #     unique_together = (("article", "tag"),)
        # verbose_name = "文章-标签"
        # verbose_name_plural = verbose_name
    def __str__(self):
        v = self.article.title + "---" + self.tag.title
        return v


#7文章详情表
#创建文本类型
#建立与文章一对一关联，一个文章，只有一个文本内容
# class ArticleDetail(models.Model):
#     nid = models.AutoField(primary_key=True)
#     content = models.TextField()
#     article = models.OneToOneField(to="Article", to_field="nid",on_delete=models.CASCADE)
#
#     class Meta:
#         verbose_name = "文章详情"
#         verbose_name_plural = verbose_name

#8点赞表
#创建布尔型是踩还是赞字段
#建立与用户一对多关联，一个用户可以点赞多篇文章
#建立与文章一对多关联，一个片文章可以被点多个赞
class ArticleUpDown(models.Model):
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to="UserInfo", null=True,on_delete=models.CASCADE)
    article = models.ForeignKey(to="Article", null=True,on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)

    # class Meta:
    #     unique_together = (("article", "user"),)
        # verbose_name = "点赞"
        # verbose_name_plural = verbose_name

#9评论表
#创建评论内容字段/评论时间字段
#建立与用户一对多关联，一个用户可以评论多篇文章
#建立与文章一对多关联，一个片文章可以被多个用户评论
#建立与自己一对多关联，一条评论可以被多人评论
class Comment(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='评论文章',to="Article", to_field="nid",on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='评论者',to="UserInfo",to_field='nid',on_delete=models.CASCADE)
    content = models.CharField(verbose_name='评论内容',max_length=255)  # 评论内容
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    parent_comment = models.ForeignKey("self", null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.content

    # class Meta:
    #     verbose_name = "评论"
    #     verbose_name_plural = verbose_name
