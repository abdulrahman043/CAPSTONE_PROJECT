from django.db import models
from django.utils import timezone

class EmailOTP(models.Model):
    user_email = models.EmailField()
    code       = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used       = models.BooleanField(default=False)

    @property
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)
