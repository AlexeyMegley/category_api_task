from rest_framework import serializers
from django.db import transaction, IntegrityError

from .models import Category
from .tree_bypassers import tree_names_generator, tree_relations_generator


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name', 'children')
        extra_kwargs = {'children': {'required': False}}

    def get_fields(self):
        fields = super(CategorySerializer, self).get_fields()
        fields['children'] = CategorySerializer(many=True, required=False)
        return fields
    
    @transaction.atomic
    def create(self, validated_data):
        # Trying not to spawn unnecessary queries to the database
        # Firstly, create all categories
        categories_to_add = []
        for name in tree_names_generator(validated_data):
            categories_to_add.append(Category(name=name))

        try:
            Category.objects.bulk_create(categories_to_add, batch_size=10000)
        except IntegrityError:
            raise serializers.ValidationError('It seems like you have cyclic dependencies in POST data')
        
        categories_from_request = Category.objects.filter(name__in=tree_names_generator(validated_data))
        name_to_id = {category.name: category.pk for category in categories_from_request}
        
        # Then add relations for all categories
        relations = []
        for parent, child in tree_relations_generator(validated_data):
            parent_id, child_id = name_to_id[parent], name_to_id[child]
            relation = Category.children.through(from_category_id=parent_id, to_category_id=child_id)
            relations.append(relation)
        
        Category.children.through.objects.bulk_create(relations, batch_size=10000)

        # return the root    
        return Category.objects.get(name=validated_data['name'])
