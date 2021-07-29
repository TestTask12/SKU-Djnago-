from django.db import models
from .category import Category
from django.contrib.auth.models import AbstractBaseUser

class Product(AbstractBaseUser):
    name = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=200, default='')
    image = models.ImageField(upload_to='uploads/products/')  #where to save image so we can use (upload_to) and give the file name

