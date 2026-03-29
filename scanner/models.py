from django.db import models
from django.contrib.auth.models import User

class ScanResult(models.Model):
    target = models.CharField(max_length=100)
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.target