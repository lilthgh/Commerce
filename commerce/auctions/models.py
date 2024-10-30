from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name=models.CharField(max_length=40)
    def __str__(self) :
        return self.name


class Bid(models.Model):
    bid =models.FloatField(default=0.0)
    user =models.ForeignKey(User,on_delete=models.CASCADE, blank=True, null=True,related_name="bids")
    def __str__(self) :
        return f"Bid of {self.bid} from {self.user}"


class Listing(models.Model):
    title=models.CharField(max_length=100)
    description=models.CharField(max_length=700)
    image=models.CharField(max_length=1000)
    price=models.ForeignKey(Bid,on_delete=models.CASCADE,blank=True, null=True,related_name="listings")
    active=models.BooleanField(default=True)
    owner=models.ForeignKey(User,on_delete=models.CASCADE, blank=True, null=True,related_name="listing")
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    category = models.CharField(max_length=400, null=True, blank=True)
    def __str__(self):  
        if self.price:  # Ensure there is a related Bid object  
            return f"{self.title}: Bid of {self.price.bid}"  
        return self.title  # Fallback if there is no price  



class Comment(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE, blank=True, null=True,related_name="comments")
    listing=models.ForeignKey(Listing,on_delete=models.CASCADE, blank=True, null=True,related_name="comments")
    message=models.CharField(max_length=300, default="No comment")
    def __str__(self) :
        return f"{self.author} ccoomented on {self.listing}"

