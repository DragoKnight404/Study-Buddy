from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Profile)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Notes)
admin.site.register(Signup)