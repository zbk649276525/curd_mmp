"""
自定义分页组件的使用方法：
    pager_obj = Pagination(request.GET.get('page',1),len(HOST_LIST),request.path_info)
    host_list = HOST_LIST[pager_obj.start:pager_obj.end]
    html = pager_obj.page_html()
    return render(request,'hosts.html',{'host_list':host_list,"page_html":html})
"""

class Pagination(object):
    """
    自定义分页
    """
    per_page_count = 2
    max_pager_count = 11
    def __init__(self,current_page,total_count,base_url,params):
    #current_page:当前页。total_count:总条数。base_url: 对应的路径。params:保存搜索条件
    # per_page_count:每页显示数据条数。max_pager_count:最大显示的页数
        try:
            current_page = int(current_page)    #页码是数字，需要转换。前端传来的是字符串
        except Exception as e:
            current_page = 1
        if current_page <=0:
            current_page = 1
        #当前的页数
        self.current_page = current_page

        # 数据总条数
        self.total_count = total_count

        # 每页显示10条数据
        self.per_page_count = self.per_page_count

        # 页面上应该显示的最大页码
        max_page_num, div = divmod(total_count, self.per_page_count) #divmod，余运算，总条数除以每页显示的条数
        if div:  #如果有余数，
            max_page_num += 1 #就给最大的页数加1
        #最大页数
        self.max_page_num = max_page_num

        # 页面上默认显示11个页面（当前页在中间）
        self.max_pager_count = self.max_pager_count
        self.half_max_pager_count = int((self.max_pager_count - 1) / 2)  #取到中间的页码

        # URL前缀
        self.base_url = base_url

        #request.GET
        import copy
        # params = copy.deepcopy(params)
        # params._mutable =True
        #包含当前列表页面素有的搜索条件
        # {source:[2,], status:[2], gender:[2],consultant:[1],page:[1]}
        # self.params[page] = 8
        # self.params.urlencode()
        # source=2&status=2&gender=2&consultant=1&page=8
        # href="/hosts/?source=2&status=2&gender=2&consultant=1&page=8"
        # href="%s?%s" %(self.base_url,self.params.urlencode())
        # self.params = params

    @property
    def start(self):    #起始页
        return (self.current_page - 1) * self.per_page_count

    @property
    def end(self):      #末尾页
        return self.current_page * self.per_page_count

# 分页器
    def page_html(self):
        # 如果总页数 <= 11
        if self.max_page_num <= self.max_pager_count:
            pager_start = 1     #起始页为1
            pager_end = self.max_page_num   #末尾页为最大页数
        # 如果总页数 > 11
        else:
            # 如果当前页 <= 5
            if self.current_page <= self.half_max_pager_count:
                pager_start = 1     #起始页为1
                pager_end = self.max_pager_count    #末尾页为最大显示的页数11
            else:
                # 当前页 + 5 > 总页码
                if (self.current_page + self.half_max_pager_count) > self.max_page_num:
                    pager_end = self.max_page_num   #末尾页为：最大页数
                    pager_start = self.max_page_num - self.max_pager_count + 1  #起始页为最大页减最大页码数+1
                else:
                    pager_start = self.current_page - self.half_max_pager_count #起始页为当前页减自身一半
                    pager_end = self.current_page + self.half_max_pager_count   #末尾页为当前页加自身一半

        page_html_list = []
        # 首页
        # self.params['page'] = 1
        first_page = '<li><a href="%s?%s">首页</a></li>'%(self.base_url,1,)
        page_html_list.append(first_page)

        #上一页
        high_page = '<li><a href="%s?page=%s">上一页</a></li>'%(self.base_url,self.current_page-1)
        if self.current_page == 1:
            high_page = '<li class="hidden"><a href="%s?page=%s">上一页</a></li>' % (self.base_url, self.current_page - 1)
            page_html_list.append(high_page)
        else:
            high_page = '<li><a href="%s?page=%s">上一页</a></li>' % (self.base_url, self.current_page - 1)
            page_html_list.append(high_page)


        #中间页
        for i in range(pager_start, pager_end + 1):
            if i == self.current_page:
                temp = '<li class="active"><a  href="%s?page=%s">%s</a></li>' % (self.base_url,i, i,)
            else:
                temp = '<li><a href="%s?page=%s">%s</a></li>' % (self.base_url,i, i,)
            page_html_list.append(temp)

        #下一页
        # fall_page = '<li><a href="%s?page=%s">下一页</a></li>'%(self.base_url,self.current_page+1)
        if self.current_page == self.max_page_num:
            fall_page = '<li class="hidden"><a href="%s?page=%s">下一页</a></li>' % (self.base_url, self.current_page + 1)
            page_html_list.append(fall_page)
        else:
            fall_page = '<li><a href="%s?page=%s">下一页</a></li>' % (self.base_url, self.current_page + 1)
            page_html_list.append(fall_page)

        #尾页
        # self.params['page'] = self.max_page_num
        last_page = '<li><a href="%s?page=%s">尾页</a></li>'%(self.base_url,self.max_page_num)
        page_html_list.append(last_page)

        return ''.join(page_html_list)