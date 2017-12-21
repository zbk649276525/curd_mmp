from stark.service import v1
from . import models

class RoleConfig(v1.StarkConfig):
    list_display =  ['id','title']
v1.site.register(models.Role,RoleConfig)

class DepartmentConfig(v1.StarkConfig):
    list_display = ['id','caption']
v1.site.register(models.Department,DepartmentConfig)

class UserInfoConfig(v1.StarkConfig):
    def display_gender(self,obj=None, is_header=False):  #obj=None:数据库没有字段   is_header=False:表头也没有
        if is_header:   #这里就需要有表头显示，  如果需要有
            return '性别'     #返回给一个 '描述'
        return obj.get_gender_display()
        #解决内容为None的问题，如果是一个 choices，通过obj.get_字段名_display()方法拿到中文名。

    def display_depart(self,obj=None, is_header=False): #obj
        if is_header:   #表头显示
            return '部门'
        return obj.depart.caption   #解决内容为None的问题, 通过对象跨表查询。

    def display_roles(self,obj=None, is_header=False):
        if is_header:   #表头显示
            return '角色'
        html = []
        role_list = obj.roles.all()
        for role in role_list:
            html.append(role.title)
       
        return ','.join(html)   #解决内容为None的问题,因为多对多关系

    # Booklist = []
    # for i in range(100):
    #     Booklist.append(models.UserInfo(name="曹操", email='anbu007@qq.com', gender='1',depart_id=1))
    # models.UserInfo.objects.bulk_create(Booklist)

    list_display = ['id','name','email',display_gender,display_depart,display_roles]

    # FilterOption('字段', 是否多选, 条件, 是否是choice)。 组合搜索的选项
    #方式1:通过字典封装， 方式2： 通过函数对象封装
    comb_filter = [
        v1.FilterOption('gender',is_choice=True),
        v1.FilterOption('depart',),
        v1.FilterOption('roles',True),    
    ]

v1.site.register(models.UserInfo,UserInfoConfig)