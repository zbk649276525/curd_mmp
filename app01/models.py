from django.db import models

# Create your models here.

class Userinfo(models.Model):
    name = models.CharField(max_length=32,verbose_name='用户名')
    
    def __str__(self):
        return self.name
    
class Role(models.Model):
    name = models.CharField(max_length=32,verbose_name='角色名')

    def __str__(self):
        return self.name
    
class UserType(models.Model):
    name = models.CharField(max_length=32,verbose_name='类型名')
    
    def __str__(self):
        return self.name