from django.shortcuts import HttpResponse
from stark.service import v1
from app01 import  models

v1.site.register(models.Userinfo)
v1.site.register(models.UserType)
v1.site.register(models.Role)

