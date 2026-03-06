# 1. 导入Django的后台管理模块
from django.contrib import admin

from web.models.blog import Blog, Tag
# 2. 导入你的自定义模型
from web.models.character import Character
from web.models.friend import Friend, Message, SystemPrompt
from web.models.user import UserProfile

# Register your models here.
# 4. 用装饰器方式注册UserProfile模型
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # 5. 设置user字段为   raw_id_fields--(输入框搜索)
    raw_id_fields = ('user',)    # 逗号不能删 - 因为要创建元组(tuple)

@admin.register(Character)      #把Character模型注册到Django后台
class CharacterAdmin(admin.ModelAdmin): #定义Character模型的管理配置类
    raw_id_fields = ('author',)     # raw_id_fields让author字段用输入框而不是下拉框显示

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    raw_id_fields = ('me','character',)
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',)
    autocomplete_fields = ('tags',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    raw_id_fields = ('friend',)

# 简单注册 - 使用默认的展示方式
admin.site.register(SystemPrompt)