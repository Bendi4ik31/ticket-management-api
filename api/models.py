from django.db import models
from django.contrib.auth.models import User

class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN',
        IN_PROGRESS = 'IN_PROGRESS',
        RESOLVED = 'RESOLVED',
        CLOSED = 'CLOSED'
    class Priority(models.TextChoices):
        LOW = 'LOW',
        MEDIUM = 'MEDIUM',
        HIGH = 'HIGH',
        CRITICAL = 'CRITICAL'
    class Meta:
        ordering = ['-created_at']
    title = models.CharField(max_length=150)
    description=models.TextField()
    status = models.CharField(choices=Status.choices,default=Status.OPEN,max_length=100)
    priority = models.CharField(choices=Priority.choices,default=Priority.MEDIUM)
    author = models.ForeignKey(User , on_delete=models.CASCADE , related_name='creaated_tickets')
    assigned_to = models.ForeignKey(User , on_delete=models.SET_NULL, null=True,blank=True , related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"