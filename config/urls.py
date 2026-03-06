from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # === 1. AUTH & JWT ===
    path('api/register/', views.register_user, name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # === 2. USERS & FOLLOW ===
    path('api/users/', views.user_list, name='user_list'),
    path('api/users/<int:pk>/', views.user_detail, name='user_detail'),
    path('api/users/<int:pk>/follow/', views.follow_user, name='follow_user'), 

    # === 3. POSTS ===
    path('api/posts/', views.post_list_create, name='post_list_create'),
    path('api/posts/<int:pk>/', views.post_detail, name='post_detail'),
    
    # === 4. LIKES ===
    path('api/posts/<int:post_id>/like/', views.like_toggle, name='like_toggle'),

    # === 5. COMMENTS ===
    path('api/posts/<int:post_id>/comments/', views.post_comments, name='post_comments'), 
    path('api/comments/', views.comment_list_create, name='comment_list_create'), 
    path('api/comments/<int:pk>/', views.comment_detail, name='comment_detail'),

    # === 6. SAVED POSTS ===
    path('api/saved/', views.get_saved_posts, name='saved_posts_list'), 
    path('api/posts/<int:pk>/save/', views.save_post, name='save_post'), 

    # === 7. MEDIA ===
    path('api/media/upload/', views.media_upload, name='media_upload'),
    path('api/media/<int:pk>/', views.media_detail, name='media_detail'),
    path('api/feed/', views.news_feed, name='news_feed'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)