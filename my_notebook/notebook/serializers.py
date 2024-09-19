from rest_framework import serializers
from .models import NoteBook, Category


class NoteBooKSerializer(serializers.ModelSerializer):
    """
    Serializer for all notebooks related operations.
    """
    category_name = serializers.StringRelatedField(source='category.name', read_only=True)

    class Meta:
        model = NoteBook
        fields = ('id', 'title', 'description', 'owner', 'category', 'created_date', 'updated_date', 'category_name')
        extra_kwargs = {
            'owner': {'required': False, 'write_only': True}, 'id': {'read_only': True}, 'category': {'write_only': True},
            'created_date': {'read_only': True}, 'updated_date': {'read_only': True}
        }


class CategorySerializer(serializers.ModelSerializer):
    """
        Serializer for create and list categories
    """
    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}}