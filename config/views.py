from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Post, Media, Comment, Like, Follow, SavedPost
from .serializers import *

User = get_user_model()

# ==========================================
# 1. USERS & AUTH
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def user_list(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method in ['PUT', 'DELETE'] and request.user != user:
        return Response({"detail": "Бұл әрекетке құқығыңыз жоқ (403)."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================
# 2. POSTS
# ==========================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list_create(request):
    if request.method == 'GET':
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method in ['PUT', 'DELETE'] and post.author != request.user:
        return Response({"detail": "Бұл сіздің постыңыз емес (403)."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================
# 3. COMMENTS
# ==========================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_comments(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'GET':
        comments = Comment.objects.filter(post=post).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_list_create(request):
    if request.method == 'GET':
        comments = Comment.objects.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_detail(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # GET үшін автор болу міндетті емес
    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
        
    # PUT және DELETE үшін міндетті түрде автор болуы керек
    if comment.author != request.user:
        return Response({"detail": "Сіздің пікіріңіз емес (403)."}, status=status.HTTP_403_FORBIDDEN)
        
    if request.method == 'PUT':
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================
# 4. LIKES
# ==========================================
@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def like_toggle(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            return Response({"message": "Лайк қойылды"}, status=status.HTTP_201_CREATED)
        return Response({"message": "Лайк бұрыннан бар"}, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Лайк басылмаған"}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 5. FOLLOWS
# ==========================================
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def follow_user(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    
    if request.method == 'GET':
        follow = Follow.objects.filter(follower=request.user, followee=target_user).first()
        if follow:
            serializer = FollowSerializer(follow)
            return Response({"following": True, "data": serializer.data})
        return Response({"following": False}, status=status.HTTP_200_OK)

    if request.user == target_user:
        return Response({"error": "Өзіңізге жазыла алмайсыз"}, status=status.HTTP_400_BAD_REQUEST)
        
    if request.method == 'POST':
        follow, created = Follow.objects.get_or_create(follower=request.user, followee=target_user)
        if created:
            return Response({"message": "Жазылдыңыз", "following": True}, status=status.HTTP_201_CREATED)
        return Response({"message": "Бұрыннан жазылғансыз"}, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        deleted, _ = Follow.objects.filter(follower=request.user, followee=target_user).delete()
        if deleted:
            return Response({"message": "Жазылу тоқтатылды", "following": False}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Жазылмағансыз"}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 6. SAVED POSTS
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved_posts(request):
    saves = SavedPost.objects.filter(user=request.user)
    serializer = SavedPostSerializer(saves, many=True)
    return Response(serializer.data)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def save_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        saved, created = SavedPost.objects.get_or_create(user=request.user, post=post)
        if created:
            return Response({"message": "Сақталды"}, status=status.HTTP_201_CREATED)
        return Response({"message": "Бұрыннан сақталған"}, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        deleted, _ = SavedPost.objects.filter(user=request.user, post=post).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Сақталмаған"}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 7. MEDIA
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def media_upload(request):
    
    post_id = request.data.get('post')
    if not post_id:
         return Response({"error": "Пост ID-і міндетті."}, status=status.HTTP_400_BAD_REQUEST)
         
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return Response({"detail": "Бөгде постқа медиа жүктей алмайсыз (403)."}, status=status.HTTP_403_FORBIDDEN)
        
    if 'file' not in request.FILES:
        return Response({"error": "Файл жіберілмеді ('file' кілті)."}, status=status.HTTP_400_BAD_REQUEST)
        
    media = Media.objects.create(post=post, file=request.FILES['file'])
    serializer = MediaSerializer(media)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def media_detail(request, pk):
    media = get_object_or_404(Media, pk=pk)
    
    if request.method == 'GET':
        serializer = MediaSerializer(media)
        return Response(serializer.data)
        
    elif request.method == 'DELETE':
        if media.post.author != request.user:
            return Response({"detail": "Құқығыңыз жоқ (403)."}, status=status.HTTP_403_FORBIDDEN)
        media.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def news_feed(request):
    following_ids = Follow.objects.filter(follower=request.user).values_list('followee_id', flat=True)
    
    posts = Post.objects.filter(author_id__in=following_ids).order_by('-created_at')
    
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)