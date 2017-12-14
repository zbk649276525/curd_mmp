from django.conf.urls import url

class  StarkConfig(object):
    def __init__(self,model_class,site):
        self.model_class = model_class
        self.site =site

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

    @property
    def urls(self):
        return (self.get_urls(),None,'stark')


site = StarkSite()