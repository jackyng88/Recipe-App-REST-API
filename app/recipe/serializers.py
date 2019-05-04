from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    # Serializer for Tag objects

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    # Serializer for Ingredient objects

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    # Serialize a recipe
    # Django REST Framework PrimaryKeyRelatedField doc -
    # https://www.django-rest-framework.org/api-guide/relations/#primarykeyrelatedfield
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingredients', 'tags', 'time_minutes',
                  'price', 'link')
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    # Serialize a recipe detail, base class is RecipeSerializer
    # The Django REST framework allows you to nest serializers within
    # eachother.
    # 'many' here means that you can have many ingredients/tags in a recipe
    # i.e. the ManyToManyField. The read_only means you can't create
    # a recipe by providing these values.
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    # Serializer for uploading images to recipes

    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
