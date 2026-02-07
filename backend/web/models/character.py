import os
import uuid
from time import localtime

from django.db import models
from django.utils import timezone
from web.models.user import UserProfile
# 上传图片处理函数
def photo_upload_to(instance, filename):
    # 1. 获取文件扩展名（如'jpg', 'png'）
    ext = filename.split('.')[-1]
    # 2. 生成10位随机字符串作为新文件名
    filename = f'{uuid.uuid4().hex[:10]}.{ext}'
    # 3. 返回存储路径：character/photos/用户ID_随机文件名
    return f'character/photos/{instance.author.user_id}_{filename}'


def background_image_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex[:10]}.{ext}'
    return f'character/backgrounds_images/{instance.author.user_id}_{filename}'

class Character(models.Model):  # models.Model----继承Django的Model基类
    # 外键关联：一个Character属于User下的UserProfile（建立模型之间的关系）
    # on_delete=models.CASCADE: 当用户被删除时，其所有角色也被删除
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # 角色名称：最大50字符的文本字段
    name = models.CharField(max_length=50)
    # 角色照片：图片字段，上传时调用photo_upload_to函数
    photo =models.ImageField(upload_to=photo_upload_to)
    # 角色简介：长文本字段，最大100000字符
    profile = models.TextField(max_length=100000)
    # 背景图片 上传时调用background_image_upload_to函数
    background_image = models.ImageField(upload_to=background_image_upload_to)

    # 创建时间：自动设为当前时间（只在创建时设置）
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)
    def __str__(self):
        """
           定义模型的字符串表示
           在Django后台、shell等地方显示时使用
        """
        # 格式：用户名 - 角色名 - 创建时间
        return f"{self.author.user.username} - {self.name} - {timezone.localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"