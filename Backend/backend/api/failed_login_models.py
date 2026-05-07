"""
Failed login attempt tracking model
"""
from django.db import models
from .models import AuthUser

class FailedLoginAttempt(models.Model):
    """Track failed login attempts for security monitoring"""

    username = models.CharField(max_length=150, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    attempt_count = models.PositiveIntegerField(default=1)

    class Meta:
        managed = True
        db_table = 'failed_login_attempt'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['username', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
        ]

    def __str__(self):
        return f"Failed login for {self.username} from {self.ip_address} at {self.timestamp}"
