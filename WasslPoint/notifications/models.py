from django.db import models
from django.conf import settings

class Notification(models.Model):
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    message    = models.CharField(max_length=255)
    url        = models.CharField(max_length=200, blank=True)
    is_read    = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification({self.user.username}): {self.message[:20]}…"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()
