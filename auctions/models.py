from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class User(AbstractUser):
    pass

class Category(models.Model):
    name=models.CharField(max_length=64, unique=True)

class Bid(models.Model):
    bid=models.IntegerField()
    owner=models.ForeignKey(User, on_delete=models.CASCADE)
    create=models.DateTimeField(default=now, editable=False)

class Listing(models.Model):
    name=models.CharField(max_length=64)
    price=models.IntegerField()
    bid=models.OneToOneField(Bid, on_delete=models.CASCADE, blank=True, null=True)
    create=models.DateTimeField(default=now, editable=False)
    description=models.CharField(max_length=500)
    category=models.ForeignKey(Category, on_delete=models.CASCADE)
    image=models.URLField(max_length=10000)
    watchlist = models.ManyToManyField(User, blank=True, related_name="listings")
    owner=models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    winner=models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    isClosed=models.BooleanField(default=False)
    
    
   


class Comment(models.Model):
    comment=models.CharField(max_length=250)
    owner=models.ForeignKey(User, on_delete=models.CASCADE)
    create=models.DateTimeField(default=now, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

                        