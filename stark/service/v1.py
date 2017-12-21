import copy,json
from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import QueryDict
from django.db.models import Q
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

#通过类函数对象来封装配置项。
class FilterOption(object):
    def __init__(self,field_name,multi=False,condition=None,is_choice=False):
        '''

        :param field_name: 字段
        :param multi: 是否多选
        :param condition: 显示数据的筛选条件
        :param is_choice: 是否是choice
        '''
        self.field_name = field_name
        self.multi =multi
        self.is_choice = is_choice
        self.condition = condition  #条件

    def get_queryset(self,_field):
        if self.condition:  #如果写了值进来
            return _field.rel.to.objects.filter(**self.condition)
        return _field.rel.to.objects.all() #否则就拿全部

    def get_choices(self,_field):
        return _field.choices   #全部都获取

#把组合搜索对象数据，封装到该类里。可迭代对象
class FilterRow(object):
    def __init__(self, option, data, request):
        self.data = data    #数据
        self.option = option    #接收的参数
        # request.GET
        self.request = request  #接收的参数，可以获取所有的url

    def __iter__(self):
        params = copy.deepcopy(self.request.GET)    #拿到request.GET 所有的对象，querydict对象。params是用户请求发来的数据。
        params._mutable = True  #要想改querydict对象，要给它设置一下
        current_id = params.get(self.option.field_name) #获取id  请求发送过来的值   字符串类型，  这里的pk是int
        current_id_list = params.getlist(self.option.field_name)    #获取多选的id。

        if self.option.field_name in params:    #如果有gender数据才删，
            # del params[self.option.field_name
            origin_list = params.pop(self.option.field_name)    #如果有就移出
            url = "{0}?{1}".format(self.request.path_info, params.urlencode())  #创建url
            yield mark_safe('<a href="{0}">全部</a>'.format(url)) #返回
            params.setlist(self.option.field_name, origin_list) # 完成url之后，在移回来
        else:
            url = "{0}?{1}".format(self.request.path_info, params.urlencode())
            yield mark_safe('<a class="active" href="{0}">全部</a>'.format(url))  #返回可以是个  a标签
        # ((1,男),(2,女))
        for val in self.data:   #谁拿到对象的值，就一点一点打印出来,通过索引取值。
            if self.option.is_choice:   #如果是choice选项,它就是“元组”，通过索引来查找
                pk, text = str(val[0]), val[1]  #pk，text 分别为： val[0],val[1]
            else:   #否则  它就是 对象，直接调用方法来查找
                pk, text = str(val.pk), str(val)
            # 当前URL？option.field_name
            # 当前URL？gender=pk
            # self.request.path_info #http://127.0.0.1:8005/arya/crm/customer/?gender=1&id=2
            # self.request.GET['gender'] = 1 # &id=2gender=1
            if not self.option.multi:
                # 单选
                params[self.option.field_name] = pk
                url = "{0}?{1}".format(self.request.path_info, params.urlencode())
                if current_id == pk:
                    yield mark_safe("<a class='active' href='{0}'>{1}</a>".format(url, text))
                else:
                    yield mark_safe("<a href='{0}'>{1}</a>".format(url, text))
            else:
                # 多选current_id_list =['1','2']
                _params = copy.deepcopy(params) #拷贝一份，可以获取所有的url,不受影响
                id_list = _params.getlist(self.option.field_name)   #当前请求的url，id

                if pk in current_id_list:   #用户传过来的值，在我们的标签选项里。
                    id_list.remove(pk)  #把自己移除掉
                    _params.setlist(self.option.field_name, id_list)    #在设置到初始值里
                    url = "{0}?{1}".format(self.request.path_info, _params.urlencode())
                    yield mark_safe("<a class='active' href='{0}'></a>".format(url, text))
                else:
                    id_list.append(pk)  #[1,2,3]
                    _params.setlist(self.option.field_name, id_list)  # params中被重新赋值
                    # 创建URL
                    url = "{0}?{1}".format(self.request.path_info, _params.urlencode()) #gender=1&id=2 按这种方式传递
                    yield mark_safe("<a href='{0}'>{1}</a>".format(url, text))  #返回可以是个  a标签

# 对Changelist优化成类封装
class ChangeList(object):
    def __init__(self, config, queryset):
        self.config = config
        # [checkbox,'id','name',edit,del]
        self.list_display = config.get_list_display()
        self.model_class = config.model_class
        self.request = config.request
        self.show_add_btn = config.get_show_add_btn()

        self.actions = config.get_actions()  # 批量删除
        self.show_actions = config.get_show_actions()
        self.comb_filter = config.get_comb_filter()  # 组合搜索，通过转接到这里。get方法

        # 搜索用
        self.show_serarch_form = config.get_show_search_form()  # 是否显示搜索栏
        self.search_form_val = config.request.GET.get(config.search_key, '')  # 是否把搜索关键字保留在搜索栏里  默认为空

        from curd_mmp.pager import Pagination
        current_page = self.request.GET.get('page', 1)
        
        total_count = queryset.count()
        pager_obj = Pagination(current_page,
                               total_count,
                               self.request.path_info,
                               self.request.GET,
                               )
        self.pager_obj = pager_obj
        self.data_list = queryset[pager_obj.start:pager_obj.end]
        

    # 改造actions
    def modify_actions(self):
        result = []
        for func in self.actions:
            temp = {'name': func.__name__, "text": func.short_desc}  # 设个函数名，用字典来封装
            result.append(temp)
        return result  # 这样以来，就成   列表里面封装的是字典格式，字典里面， name就是函数名

    def add_url(self):
        return self.config.get_add_url()

    def show_add_btn(self):
        return self.config.get_show_add_btn()

    def head_list(self):
        '''
        构造表头
        :return:
        '''
        result = []
        # [checkbox,'id','name',edit,del]
        for field_name in self.list_display:
            if isinstance(field_name, str):
                # 根据类和字段名称，获取字段对象的verbose_name
                verbose_name = self.model_class._meta.get_field(field_name).verbose_name
            else:
                verbose_name = field_name(self.config, is_header=True)
            result.append(verbose_name)
        return result

    def body_list(self):
        # 处理表中的数据
        # [UserInfoObj.UserInfoObj,UserInfoObj,UserInfoObj,]
        # [UserInfo(id=1,name='alex',age=18),UserInfo(id=2,name='alex2',age=181),]
        data_list = self.data_list
        new_data_list = []
        for row in data_list:
            # row 是 Userinfo(id=2,name='alex',age=18)
            # row id,row name, row age
            temp = []
            for field_name in self.list_display:
                if isinstance(field_name, str):
                    val = getattr(row, field_name)
                else:
                    val = field_name(self.config, row)
                temp.append(val)
            new_data_list.append(temp)
        return new_data_list

    # 组合搜搜  给前端进行循环显示数据用（生成器函数），这里返回什么，前端就能看到什么。
    def gen_comb_filter(self):
        '''
        生成器函数
        :return:
        '''
        # ['gender','depart','roles']
        # self.model_class = models.UserInfo
        data_list = []

        from django.db.models import ForeignKey, ManyToManyField
        for option in self.comb_filter:     #for循环拿到配置项的数据
            _field = self.model_class._meta.get_field(option.field_name)    #拿到类里面的字段
            if isinstance(_field, ForeignKey):  #判断"_field"字段是否为  外键
                # 获取当前字段depart,关联的表 Department表并获取其所有数据
                # print(field_name,_field.rel.to.objects.all())     # "_fiedls.rel  可以找到类"
                row = FilterRow(option, option.get_queryset(_field), self.request)  #拿到过滤后的数据
            elif isinstance(_field, ManyToManyField):
                # print(field_name,_field.rel,to objects.all())
                # data_list.append(_field.rel.to.objects.all())
                row = FilterRow(option, option.get_queryset(_field), self.request)
            else:
                # data_list.append(_field.choices)
                row = FilterRow(option, option.get_choices(_field), self.request)
            # row是个可迭代对象
            yield row

# 用于为每一个类生成url对应关系，并编写视图函数处理用户请求
class StarkConfig(object):
    def __init__(self, model_class, site):
        self.model_class = model_class
        self.site = site
        self.request = None
        self._query_param_key = "_listfilter"
        self.search_key = "_q"  # 统一使用方法

    # 1. 定制列表页面显示的列
    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return '选择'
        return mark_safe('<input type="checkbox" name="pk" value="%s" />' % (obj.id,))

    # 编辑方法
    def edit(self, obj=None, is_header=False):
        if is_header:
            return '编辑'
        # 获取条件
        query_str = self.request.GET.urlencode()  # 拿到一个字符串
        if query_str:
            # 重新构造
            params = QueryDict(mutable=True)  # 设成可修改状态
            params[self._query_param_key] = query_str  # 重新赋值
            return mark_safe('<a href="%s?%s">编辑</a>' % (self.get_change_url(obj.id), params.urlencode(),))

        return mark_safe('<a href="%s">编辑</a>' % (self.get_change_url(obj.id),))

    # 删除方法
    def delete(self, obj=None, is_header=False):
        if is_header:
            return '删除'
        # 获取条件
        query_str = self.request.GET.urlencode()
        if query_str:
            # 重新构造
            params = QueryDict(mutable=True)  # 设置成可改
            params[self._query_param_key] = query_str
            print(query_str, '============')
            return mark_safe('<a href="%s?%s">删除</a>' % (self.get_delete_url(obj.id), params.urlencode(),))
        return mark_safe('<a href="%s">删除</a>' % (self.get_delete_url(obj.id),))

    list_display = []

    def get_list_display(self):
        data = []
        if self.list_display:
            data.extend(self.list_display)
            data.append(StarkConfig.edit)
            data.append(StarkConfig.delete)
            data.insert(0, StarkConfig.checkbox)
        return data

    # 2. 是否显示添加按钮
    show_add_btn = True
    def get_show_add_btn(self):
        return self.show_add_btn

    # 3, model_form_class 公共页面，编辑页面就需要调用它。
    model_form_class = None
    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class
        # 方法一：基于类创建ModelForm
        from django.forms import ModelForm
        class TestModelForm(ModelForm):
            class Meta:
                model = self.model_class
                fields = "__all__"

        return TestModelForm

        # 方法二：type创建TestModelForm
        # meta = type('Meta',(object,),{'model':self.model_class,'fields':'__all__'})
        # TestModelForm = type('TestModelForm',(ModelForm,),{'Meta':meta})
        # return TestModelForm

    # 4.关键字搜索
    show_search_form = False
    def get_show_search_form(self):  # 设置搜索栏是否显示  前端用的
        return self.show_search_form

    search_fields = []  # 设个空列表，用于存关键字，默认没有搜索条件
    def get_search_fields(self):  # 到底显示哪些字段   后台用的
        result = []
        if self.search_fields:
            result.extend(self.search_fields)

        return result

    def get_search_condition(self):  # 过滤条件
        key_word = self.request.GET.get(self.search_key)
        search_fiedls = self.get_search_fields()  # 拿到搜索关键字

        condition = Q()  # Q查询， and和or
        condition.connector = 'or'  # 设置条件里相连关系为 or
        if key_word and self.get_show_search_form():  # get_show_search_form 表示：当设为True才有反应
            for field_name in search_fiedls:  # 循环关键字，那到关键字条件
                condition.children.append((field_name, key_word))  # 把关键字条件添加到查询框里
        return condition

    # 5.actions 定制  可配置
    show_actions = False  # 是否显示批量删除框

    def get_show_actions(self):
        return self.show_actions

    actions = []  # 设个空列表

    def get_actions(self):
        result = []
        if self.actions:
            result.extend(self.actions)
        return result

    # 6.组合搜索
    comb_filter = []    #设个空列表

    def get_comb_filter(self):  #
        result = []     #设个空列表
        if self.comb_filter:    #如果有请求
            result.extend(self.comb_filter)     #列表扩张请求过来的需求
        return result   #返回

    # --------------- url  相关-------------------------
    # 装饰器
    def wrap(self, view_func):
        def inner(request, *args, **kwargs):
            self.request = request
            return view_func(request, *args, **kwargs)

        return inner

    def get_urls(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name)
        url_patterns = [
            url(r'^$', self.wrap(self.changelist_view), name="%s_%s_changelist" % app_model_name),
            url(r'^add/$', self.wrap(self.add_view), name="%s_%s_add" % app_model_name),
            url(r'^(\d+)/delete/$', self.wrap(self.delete_view), name="%s_%s_delete" % app_model_name),
            url(r'^(\d+)/change/$', self.wrap(self.change_view), name="%s_%s_change" % app_model_name),
        ]
        url_patterns.extend(self.extra_url())
        return url_patterns

    def extra_url(self):
        return []

    @property
    def urls(self):
        return self.get_urls()

    def get_change_url(self, nid):
        name = "stark:%s_%s_change" % (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        edit_url = reverse(name, args=(nid,))
        return edit_url

    def get_list_url(self):
        name = "stark:%s_%s_changelist" % (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        edit_url = reverse(name)
        return edit_url

    def get_add_url(self):
        name = "stark:%s_%s_add" % (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        edit_url = reverse(name)
        return edit_url

    def get_delete_url(self, nid):
        name = "stark:%s_%s_delete" % (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        edit_url = reverse(name, args=(nid,))
        return edit_url

    # -----------处理请求的方法-----------------

    def changelist_view(self, request, *args, **kwargs):
        # 处理表头
        # head_list = []
        # for field_name in self.get_list_display():
        #     if isinstance(field_name, str):
        #         # 根据类和字段名称，获取字段对象的verbose_name
        #         verbose_name = self.model_class._meta.get_field(field_name).verbose_name
        #     else:
        #         verbose_name = field_name(self, is_header=True)
        #     head_list.append(verbose_name)

        # 处理分页
        # from curd_mmp.pager import Pagination
        # current_page = request.GET.get('page', 1)
        # total_count = self.model_class.objects.all().count()
        # pager_obj = Pagination(current_page, total_count, request.path_info, per_page_count=10)

        # 处理表中的数据
        # [ Obj,UserInfoObj,UserInfoObj,UserInfoObj,]
        # [ UserInfo(id=1,name='alex',age=18),UserInfo(id=2,name='alex2',age=181),]
        # data_list = self.model_class.objects.all()[pager_obj.start:pager_obj.end]
        # new_data_list = []
        # for row in data_list:
        #     # row 是 Userinfo(id=2,name='alex2'，age=191)
        #     # row.id,row.name.row.age
        #     temp = []
        #     for field_name in self.get_list_display():
        #         if isinstance(field_name, str):
        #             val = getattr(row, field_name)  # 反射
        #         else:
        #             val = field_name(self, row)
        #         temp.append(val)
        #     new_data_list.append(temp)

        # #分页
        # try:
        #     page = request.GET.get('page', 1)
        # except PageNotAnInteger:
        #     page = 1
        # p = Paginator(new_data_list, 10, request=request)
        # # 实例化一个分页器对象，需要三个参数，第一个是一个可迭代对象，第二个是分多少页
        # orgs = p.page(page)

        # return render(request, 'stark/changelist.html',
        #               {'data_list': new_data_list,
        #                'head_list': head_list,
        #                'add_url': self.get_add_url(),
        #                'show_add_btn': self.get_show_add_btn(),
        #                'pager_obj': pager_obj,
        #                })

        # 批量删除
        if request.method == "POST" and self.get_show_actions():  # 批量删除和初始化，post提交，拿到数据
            func_name_str = request.POST.get('list_action')  # 拿到数据id,函数名称的字符串
            action_func = getattr(self, func_name_str)  # getattr反射，找到action函数。
            ret = action_func(request)  # 执行函数，可以传参数
            # if ret: #如果有返回值，可以按照自己的要求，来返回其它界面
            #     return ret

        # 组合搜索 根据URL中传递的参数，对数据进行筛选
        comb_condition = {} #用来构造搜索条件
        option_list = self.get_comb_filter()    #用来做判断
        for key in request.GET.keys():  #通过拿 key， request.GET.keys 传多个参数我们都可以拿到

            value_list = request.GET.getlist(key)
            flag = False
            for option in option_list:
                if option.field_name == key:
                    flag = True
                    break
            if flag:    #如果在我们的配置里
                comb_condition["%s__in" % key] = value_list  #就需要构造条件       {'gender__in':[1],'depart__in:':[5,8]}
        print(comb_condition,'*********************88')
        queryset = self.model_class.objects.filter(self.get_search_condition()).filter(
            **comb_condition).distinct()  # 过滤条件
        c1 = ChangeList(self, queryset)
        return render(request, 'stark/changelist.html', {'c1': c1})

    def add_view(self, request, *args, **kwargs):

        model_form_class = self.get_model_form_class()
        # _popbackid = request.GET.get('_popbackid')  #pop 返回的id
        if request.method == "GET":
            form = model_form_class()
            return render(request, 'stark/add_view.html', {'form': form})
        else:
            form = model_form_class(request.POST)
            if form.is_valid():
                #数据库中创建数据
                new_obj = form.save()
                # if _popbackid:
                    #是popup 请求
                    #render一个页面，写自执行函数
                    # result = {'id':new_obj.pk,'text':str(new_obj),'popbackid':_popbackid}
                    # return render(request,'stark/popup_response.html',{'json_result':json.dumps(result,ensure_ascii=False)})
                # else:
                return redirect(self.get_list_url())
            return render(request, 'stark/add_view.html', {'form': form})

    def delete_view(self, request, nid, *args, **kwargs):
        self.model_class.objects.filter(pk=nid).delete()
        list_query_str = request.GET.get(self._query_param_key)  # 把路径数据取到
        list_url = "%s?%s" % (self.get_list_url(), list_query_str,)  # 实行拼接
        return redirect(list_url)

    def change_view(self, request, nid, *args, **kwargs):
        obj = self.model_class.objects.filter(pk=nid).first()
        if not obj:
            return redirect(self.get_list_url())
        model_form_class = self.get_model_form_class()
        # GET,显示标签+默认值
        if request.method == 'GET':
            form = model_form_class(instance=obj)
            return render(request, 'stark/change_view.html', {'form': form})
        else:
            form = model_form_class(instance=obj, data=request.POST)
            if form.is_valid():
                form.save()
                list_query_str = request.GET.get(self._query_param_key)
                list_url = "%s?%s" % (self.get_list_url(), list_query_str,)
                return redirect(list_url)
            return render(request, 'stark/change_view.html', {'form': form})

# 代指一个容器，用户放置处理请求对应关系。
class StarkSite(object):
    '''
    注册

    '''

    def __init__(self):
        self._registry = {}  # 第3步：设一个空的字典。 self._registry

    def register(self, model_class, stark_config_class=None):
        # model_class:表名  stark_config_class: 自定义
        if not stark_config_class:  # 如果没有自定类
            stark_config_class = StarkConfig  # 默认执行内部自带的。
        self._registry[model_class] = stark_config_class(model_class, self)
        # {"model_class":"StarkConfig(object)" }

    def get_urls(self):
        url_pattern = []  # 自定一个空列表

        for model_class, stark_config_obj in self._registry.items():  #
            # 为每一个类，创建4个url
            app_name = model_class._meta.app_label  # 应用名
            model_name = model_class._meta.model_name  # 类名

            curd_url = url(r'^%s/%s/' % (app_name, model_name,), (stark_config_obj.urls, None, None))
            url_pattern.append(curd_url)
        return url_pattern

    @property
    def urls(self):
        return (self.get_urls(), None, 'stark')

# 调用类方法。
site = StarkSite()  # 第2步
