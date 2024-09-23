from django.db import models
from django.contrib.auth import get_user_model as User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class NoteBook(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User(), on_delete=models.CASCADE, related_name='user_notebooks')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
