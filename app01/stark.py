from django.shortcuts import HttpResponse,redirect
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

    show_search_form = True
    search_fields = ['name__contains','email__contains']  #设置搜索关键字   加 __contains 为模糊搜索

    show_actions = True

  

    def multi_del(self,request):    #批量删除
        print(request.POST,'............')
        pk_list = request.POST.getlist('pk')    #找到对应值
        self.model_class.objects.filter(id__in=pk_list).delete()    #对比数据，执行删除
        #return HttpResponse('删除成功')
        return redirect("http://baidu.com")
    multi_del.short_desc = "批量删除"
    
    def multi_init(self,request):
        pk_list = request.POST.getlist('pk')
        return HttpResponse('初始化成功')
    multi_init.short_desc = "批量初始化"

    actions = [multi_del,multi_init]  #装在函数


    #批量插入
    # Booklist = []
    # for i in range(100):
    #     Booklist.append(models.Userinfo(name="暗部忍者", age=30, email='anbu007@qq.com',hobby='偷窥',ut_id=1))
    # models.Userinfo.objects.bulk_create(Booklist)

    # def extra_url(self):
    #     url_list = [
    #         url(r'^xxx/$',self.func),
    #     ]
    #     return url_list
    #
    # def func(self,request):
    #     return HttpResponse('扩展页面')
v1.site.register(models.Userinfo,UserInfoConfig)   
#models.Useerinfo:表名  UserinfoConfig:自定义类，继承一个可处理url视图函数的类。

class RoleConfig(v1.StarkConfig):
    list_display =['name',]
v1.site.register(models.UserType,RoleConfig)

class UserTypeConfig(v1.StarkConfig):
    list_display = ['id','name']
v1.site.register(models.Role,UserTypeConfig)

