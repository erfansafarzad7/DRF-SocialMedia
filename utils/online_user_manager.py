from django.core.cache import caches
from django.utils import timezone

import json


class OnlineUserManager:
    """
    Manages the online status of users using Django's cache system.

    This class provides methods to mark users as online/offline, check if a user is online,
    and retrieve a list of online users. The online status is stored in the cache with a timeout
    period to indicate when the user's status should expire.
    """
    ONLINE_TIMEOUT = 300  # Timeout in seconds (5 minutes)

    @classmethod
    def mark_user_online(cls, user_id):
        """
        Marks a user as online by storing their status in the cache.

        This method saves the user's online status with the current timestamp in the cache.
        The status will expire after a set timeout.
        """
        online_cache = caches['online_users']
        online_cache.set(
            f'user:{user_id}:status',
            json.dumps({
                'online_at': timezone.now().isoformat(),
                'is_online': True
            }),
            timeout=cls.ONLINE_TIMEOUT  # The online status will expire after this timeout
        )

    @classmethod
    def mark_user_offline(cls, user_id):
        """
        Marks a user as offline by deleting their status from the cache.
        """
        online_cache = caches['online_users']
        online_cache.delete(f'user:{user_id}:status')

    @classmethod
    def get_online_users(cls):
        """
        Retrieves a list of all online users by checking the cache.
        """
        online_cache = caches['online_users']
        online_keys = online_cache.keys('user:*:status')  # Get all keys related to user status
        return [int(key.split(':')[1]) for key in online_keys]  # Extract user IDs from the cache keys

    @classmethod
    def is_user_online(cls, user_id):
        """
        Checks if a specific user is online.

        This method verifies if the user's status is present in the cache. If the status is found,
        it means the user is online.
        """
        online_cache = caches['online_users']
        return online_cache.get(f'user:{user_id}:status') is not None  # Check if the user's status is in the cache
