
import uuid

from django.db import models
from django.utils import timezone

from web.models.user import UserProfile

def blog_cover_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex[:10]}.{ext}'
    return f'blog/cover/{instance.author.user_id}_{filename}'

class Tag(models.Model):
    name = models.CharField(max_length=10, unique=True,verbose_name="标签名")
    def __str__(self):
        return self.name

class Blog(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name='blogs')
    title = models.CharField(max_length=100,verbose_name='标题')
    content=models.TextField(verbose_name="正文")
    cover_photo=models.ImageField(upload_to=blog_cover_upload_to,blank=True,null=True,verbose_name='文章封面')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签')
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['-create_time']     #按照时间倒序
    #标签，多对多
    # ManyToManyField - 多对多关系   Tag - 关联的模型  blank=True - 允许为空
    def __str__(self):
        return f"{self.title} - {self.author.user.username}   -   {self.create_time}   -   {timezone.localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"