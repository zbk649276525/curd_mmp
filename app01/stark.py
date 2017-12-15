from django.shortcuts import HttpResponse
from django.utils.safestring import mark_safe
from stark.service import v1
from app01 import  models
from django.conf.urls import url
from django.forms import ModelForm

class UserInfoConfigForm(ModelForm):
    class Meta:
        model = models.Userinfo
        fields = "__all__"
        error_messages = {
            "name":{"required":"用户名不能为空"},
            "age":{"required":"年龄不能为空"},
            "email":{"required":"邮箱不能为空"},
            "ut":{"required":"不能为空"},
            "hobby":{"required":"不能为空"},
        }
class UserInfoConfig(v1.StarkConfig):
    list_display =['id','name','age','email','ut_id']

    show_add_btn = True

    model_form_class = UserInfoConfigForm

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

