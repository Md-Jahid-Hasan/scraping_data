from django.contrib import admin
from django.contrib.auth import get_user_model as User

admin.site.register(User())