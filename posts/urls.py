from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet,
    CommentCreateView,
    CommentDetailView,
    ReactionToggleView,
    TagView
)

router = DefaultRouter()
router.register(r'posts', PostViewSet)

urlpatterns = [
    path('comments/create/', CommentCreateView.as_view(), name='comment_create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment_detail'),
    path('reaction/', ReactionToggleView.as_view(), name='reaction'),
    path('tags/', TagView.as_view(), name='reaction'),

    path('', include(router.urls)),
]
