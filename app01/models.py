from django.db import models

# Create your models here.

class Userinfo(models.Model):
    name = models.CharField(max_length=32,verbose_name='用户名')
    age = models.IntegerField(verbose_name='年龄',blank=True,null=True)
    email = models.EmailField(max_length=32,verbose_name='邮箱',blank=True,null=True)
    hobby = models.CharField(max_length=32,verbose_name='爱好',blank=True,null=True)
    ut = models.ForeignKey(to='UserType',verbose_name='村落',blank=True,null=True)

    
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