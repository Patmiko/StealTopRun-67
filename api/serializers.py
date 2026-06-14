from rest_framework import serializers
from main.models import User, Game, Category, SpeedrunType, Speedrun

class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']

class PublicCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class PublicGameSerializer(serializers.ModelSerializer):
    categories = PublicCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ['id', 'name', 'release_date', 'description', 'image', 'categories']

class PublicSpeedrunTypeSerializer(serializers.ModelSerializer):
    game = PublicGameSerializer(read_only=True)
    
    class Meta:
        model = SpeedrunType
        fields = ['id', 'name', 'description', 'game']

class PublicSpeedrunSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    speedrun_type = PublicSpeedrunTypeSerializer(read_only=True)
    
    embed_url = serializers.ReadOnlyField()
    formatted_time = serializers.ReadOnlyField()

    class Meta:
        model = Speedrun
        fields = [
            'id', 'url', 'embed_url', 'time', 'formatted_time', 
            'date', 'speedrun_type', 'user']