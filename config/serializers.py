from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Media, Comment, Like, Follow, SavedPost, Story

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'avatar', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'post', 'file', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    media = MediaSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'author_name', 'caption', 'media', 'created_at']
        read_only_fields = ['author']

class NoteSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = ['id', 'author', 'author_name', 'caption', 'media', 'created_at']
        read_only_fields = ['author']

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["id", "user", "image", "video", "created_at", "expires_at"]

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_name', 'post', 'text', 'created_at']
        read_only_fields = ['author', 'post']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']

class FollowSerializer(serializers.ModelSerializer):
    follower_name = serializers.ReadOnlyField(source='follower.username')
    followee_name = serializers.ReadOnlyField(source='followee.username')

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followee', 'follower_name', 'followee_name', 'created_at']

class SavedPostSerializer(serializers.ModelSerializer):
    post_title = serializers.ReadOnlyField(source='post.caption')

    class Meta:
        model = SavedPost
        fields = ['id', 'user', 'post', 'post_title', 'created_at']
