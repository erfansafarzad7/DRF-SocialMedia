from celery import shared_task
from django.shortcuts import get_object_or_404


@shared_task
def notify_followers(post_id):
    from accounts.models import Notification
    from posts.models import Post

    post_obj = get_object_or_404(Post, id=post_id)
    author = post_obj.author

    # Get author followers
    followers = author.followers.all()
    followers = [f.follower for f in followers]  # CustomUser Objects

    notification = Notification.objects.create(
        message=f'"{author.username}" Has Shared New Post!'
    )

    # Add followers to target users
    notification.target_users.add(*followers)
