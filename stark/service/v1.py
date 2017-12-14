from django.conf.urls import url
from django.shortcuts import HttpResponse,render

class  StarkConfig(object):
    list_display = []

    def __init__(self,model_class,site):
        self.model_class = model_class
        self.site =site

    def get_urls(self):
        app_model_name = (self.model_class._meta.app_label,self.model_class._meta.model_name)
        url_patterns = [
            url(r'^$', self.changelist_view, name="%s/%s_changelist" % app_model_name),
            url(r'^add/$', self.add_view, name="%s/%s_add" % app_model_name),
            url(r'^(\d+)/delete/$', self.delete_view, name="%s/%s_delete" % app_model_name),
            url(r'^(\d+)/change/$', self.change_view, name="%s/%s_change" % app_model_name),
        ]
        return url_patterns

    @property
    def urls(self):
        return self.get_urls()

    #-----------处理请求的方法-----------------

    def changelist_view(self,request,*args,**kwargs):
        #处理表头
        head_list = []
        for field_name in self.list_display:
            if isinstance(field_name,str):
                #根据类和字段名称，获取字段对象的verbose_name
                verbose_name = self.model_class._meta.get_field(field_name).verbose_name
            else:
                verbose_name = field_name(self,is_header=True)
            head_list.append(verbose_name)
            
        #处理表中的数据
        # [ UserInfoObj,UserInfoObj,UserInfoObj,UserInfoObj,]
        # [ UserInfo(id=1,name='alex',age=18),UserInfo(id=2,name='alex2',age=181),]
        data_list = self.model_class.objects.all()
        new_data_list = []
        for row in data_list:
            #row 是 Userinfo(id=2,name='alex2'，age=191)
            #row.id,row.name.row.age
            temp=[]
            for field_name in self.list_display:
                if isinstance(field_name,str):
                    val = getattr(row,field_name) #反射
                else:
                    val = field_name(self,row)
                temp.append(val)
            new_data_list.append(temp)
        return render(request,'stark/changelist.html',{'data_list':new_data_list,'head_list':head_list})
    
    def add_view(self,request,*args,**kwargs):
        return HttpResponse('添加')
    def delete_view(self,request,*args,**kwargs):
        return HttpResponse('删除')
    def change_view(self,request,*args,**kwargs):
        return HttpResponse('修改')




class StarkSite(object):
    '''
    注册
    '''
    def __init__(self):
        self._registry = {}
    def register(self,model_class,stark_config_class=None):
        if not stark_config_class:
            stark_config_class =StarkConfig
        self._registry[model_class] = stark_config_class(model_class,self)
        #{"model_class":"StarkConfig(object)" }

    def get_urls(self):
        url_pattern = []

        for model_class,stark_config_obj in self._registry.items():
            #为每一个类，创建4个url
            app_name = model_class._meta.app_label #应用名
            model_name = model_class._meta.model_name #类名

            curd_url = url(r'^%s/%s/'%(app_name,model_name,),(stark_config_obj.urls,None,None))
            url_pattern.append(curd_url)
        return url_pattern

    @property
    def urls(self):
        return (self.get_urls(),None,'stark')


site = StarkSite()