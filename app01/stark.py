from django.shortcuts import HttpResponse
from django.utils.safestring import mark_safe
from stark.service import v1
from app01 import  models

class UserInfoConfig(v1.StarkConfig):
    def checkbox(self,obj=None,is_header=False):
        if is_header:
            return '选择'
        return mark_safe('<input type="checkbox" name="pk" value="%s" />' %(obj.id,))
    def edit(self,obj=None,is_header=False):
        if is_header:
            return '编辑'
        return mark_safe('<a href="/edit/%s">编辑</a>' %(obj.id,))
    list_display =[checkbox,'id','name',edit]
v1.site.register(models.Userinfo,UserInfoConfig)

class RoleConfig(v1.StarkConfig):
    list_display =['name',]
v1.site.register(models.UserType,RoleConfig)

class UserTypeConfig(v1.StarkConfig):
    list_display = ['id','name']
v1.site.register(models.Role,UserTypeConfig)

