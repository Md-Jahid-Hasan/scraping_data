from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from .models import NoteBook, Category
from .serializers import NoteBooKSerializer, CategorySerializer
from my_notebook.custom_permissions import IsOwnerOrReadOnly


class ListCreateNotebook(ListCreateAPIView):
    """
    It returns a list of Notebooks. Also, responsible for create a notebook by validating the category
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NoteBooKSerializer
    queryset = NoteBook.objects.all()

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        category = request.data.get('category')
        is_category_exists = Category.objects.filter(id=category).exists()
        if not is_category_exists:
            return Response({"error": "Category not found"}, status=HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class HandleNoteBook(RetrieveUpdateDestroyAPIView):
    """This view is responsible for retrieve, update(both put and patch) and delete a notebook. It also maintains that
        authorized user should be the one who create the notebook.
        Here update method is override because if user want to update category then it should have validated the category
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = NoteBooKSerializer
    queryset = NoteBook.objects.all()

    def update(self, request, *args, **kwargs):
        category = request.data.get('category', None)

        if category:
            is_category_exists = Category.objects.filter(id=category).exists()
            if not is_category_exists:
                return Response({"error": "Category not found"}, status=HTTP_400_BAD_REQUEST)
        return super(HandleNoteBook, self).update(request, *args, **kwargs)


class ListCreateCategory(ListCreateAPIView):
    """
    This view is responsible for list and create categories with name and id field
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def create(self, request, *args, **kwargs):
        category = request.data.get('name')
        is_category_exists = Category.objects.filter(name__iexact=category).exists()

        if is_category_exists:
            return Response({"error": "Category with same name already exists"}, status=HTTP_400_BAD_REQUEST)
        return super(ListCreateCategory, self).create(request, *args, **kwargs)