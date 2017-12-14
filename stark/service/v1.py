from django.conf.urls import url
from django.shortcuts import HttpResponse

class  StarkConfig(object):
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

    def changelist_view(self,request,*args,**kwargs):
        return HttpResponse('列表')
    def add_view(self,request,*args,**kwargs):
        return HttpResponse('添加')
    def delete_view(self,request,*args,**kwargs):
        return HttpResponse('删除')
    def change_view(self,request,*args,**kwargs):
        return HttpResponse('修改')

    @property
    def urls(self):
        return self.get_urls()


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