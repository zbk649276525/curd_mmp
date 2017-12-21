from django.urls import reverse
from django.template import Library
from stark.service.v1 import site

register = Library()

@register.inclusion_tag('stark/form.html')
def form(model_form_obj):
    new_form = []   #设个空列表
    for bfield in model_form_obj:   #for循环，取到所有字段
        temp = {'is_popup':False,'item':bfield} #设个字典，给个属性。
        #field是ModelForm 读取对应的models类，然后根据每一个数据库字段,生成form字段
        from django.forms.boundfield import BoundField
        from django.db.models.query import  QuerySet
        from django.forms.models import ModelChoiceField
        if isinstance(bfield.field,ModelChoiceField):   #判断：要么是FK，要么是 M2M
            related_class_name = bfield.field.queryset.model    #queryset: 拿到所有类字段数据，（和fk关联的类名）
            if related_class_name in site._registry:    #判断是否已经注册了url
                app_model_name = related_class_name._meta.app_label,related_class_name._meta.model_name
                #根据类名反向生成拿到url  “app_model_name”拿到一个元组
                base_url = reverse("stark:%s_%s_add"%app_model_name)    #reverse开始反向生成url ：前缀+app名称+类名+add
                popurl = "%s?_popbackid=%s"%(base_url,bfield.auto_id)   #返回数据时，用于接收的id。auto_id 是内部自动拼接的。
                temp['is_popup'] = True     #如果是 FK，或者M2M
                temp['popup_url'] = popurl   #后台生成url，接着传到前端，生成url
        new_form.append(temp)   #添加进来
    return {'form':new_form}    #把new_form传过去










