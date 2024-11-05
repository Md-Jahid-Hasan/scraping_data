from django.urls import path
from .views import ListCreateNotebook, HandleNoteBook, ListCreateCategory

app_name = 'notebook'

urlpatterns = [
    path('', ListCreateNotebook.as_view(), name='notebook'),
    path('<int:pk>/', HandleNoteBook.as_view(), name='handle_notebook'),
    path('category/', ListCreateCategory.as_view(), name='category'),
]