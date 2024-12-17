from django.urls import path
from .views import (
    ChatCreateView,
    ChatListView,
    ChatDetailView,
    ChatEditView,
    ChatMessagesView,
    OnlineUsersView
)


urlpatterns = [
    path('', ChatListView.as_view(), name='chat_list'),
    path('create/', ChatCreateView.as_view(), name='chat_create'),
    path('<int:pk>/', ChatDetailView.as_view(), name='chat_detail'),
    path('<int:pk>/edit/', ChatEditView.as_view(), name='chat_edit'),
    path('<int:chat_id>/messages/', ChatMessagesView.as_view(), name='chat_messages'),

    path('online-users/', OnlineUsersView.as_view(), name='online_users'),
]
