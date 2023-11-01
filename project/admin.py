from django.contrib import admin
from .models import User, Post, Recycle_Event

# Register your models here.
admin.site.register(User),
admin.site.register(Post),
admin.site.register(Recycle_Event),