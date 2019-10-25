from django.shortcuts import get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(GenericViewSet, CreateModelMixin, ListModelMixin):

    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def retrieve(self, request, pk=None):
        category = get_object_or_404(self.queryset, pk=pk)
        return Response(category.extract_relations_dict())
