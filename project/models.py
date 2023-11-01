from django.db import models
from django.forms import CharField
from django.utils import timezone

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=30)
    phone = models.CharField(max_length=10, default='')
    zipcode = models.CharField(max_length=1000)
    password = models.CharField(max_length=1000)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    salt = models.CharField(max_length=1023)
    def __str__(self):
        return '%s - %s' % (self.username, self.created_at)
    
class Post(models.Model):
    SALE_CHOICES = [
        (1, 'Sale'),
        (2, 'Donation')
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="media")
    description = models.CharField(max_length=500, blank=True)
    sale_type = models.IntegerField(default=1, choices=SALE_CHOICES)
    date_posted = models.DateTimeField(auto_now_add=True)
    # If sale type is auction, the price field will have the value of the floor price.
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.title} - {self.seller.username}'
    
class Recycle_Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recycleevents")
    recycler = models.CharField(max_length=400)
    date_of = models.DateField()
    date_posted = models.DateTimeField(auto_now_add=True)
    zipcode = models.CharField(max_length=1000)
    instructions = models.CharField(max_length=500, blank=True)
    fee = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.recycler} - {self.date_of}'
