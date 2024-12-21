from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Follow, Notification


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    """
    Signal to create a notification when a user follows another user.
    """
    if created:  # Only for new follow relationships
        notif = Notification.objects.create(
            message=f"{instance.follower.username} has started following you."
        )
        notif.target_users.add(instance.following)
        notif.save()
