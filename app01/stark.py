from django.shortcuts import HttpResponse
from django.utils.safestring import mark_safe
from stark.service import v1
from app01 import  models
from django.conf.urls import url

class UserInfoConfig(v1.StarkConfig):

    list_display =['id','name',]

    # def extra_url(self):
    #     url_list = [
    #         url(r'^xxx/$',self.func),
    #     ]
    #     return url_list
    #
    # def func(self,request):
    #     return HttpResponse('扩展页面')
v1.site.register(models.Userinfo,UserInfoConfig)

class RoleConfig(v1.StarkConfig):
    list_display =['name',]
v1.site.register(models.UserType,RoleConfig)

class UserTypeConfig(v1.StarkConfig):
    list_display = ['id','name']
v1.site.register(models.Role,UserTypeConfig)

