from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class ChatRoom(models.Model):
    """
    Represents a chat room between users
    Can be 1-on-1 (therapist-client) or group (community)
    """
    ROOM_TYPES = [
        ('therapy', 'Therapy Session'),
        ('community', 'Community Chat'),
        ('group', 'Group Session'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='therapy')
    participants = models.ManyToManyField(User, related_name='chat_rooms', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For therapy sessions - link to specific appointment if needed
    appointment = models.ForeignKey(
        'appointments.Appointment', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='chat_room'
    )
    
    class Meta:
        ordering = ['-updated_at']
        
    def __str__(self):
        if self.name:
            return self.name
        participants_names = ", ".join([user.username for user in self.participants.all()[:2]])
        return f"Chat: {participants_names}"
    
    @property
    def last_message(self):
        return self.messages.filter(is_deleted=False).last()
    
    def get_other_participant(self, current_user):
        """Get the other participant in a 1-on-1 chat"""
        return self.participants.exclude(id=current_user.id).first()


class Message(models.Model):
    """
    Individual messages within a chat room
    """
    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField(blank=True)
    
    # For file/image messages
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    
    # Message metadata
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    
    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    # For reply/thread functionality
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['sent_at']
        
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        # Update the chat room's updated_at timestamp
        super().save(*args, **kwargs)
        self.room.updated_at = timezone.now()
        self.room.save(update_fields=['updated_at'])


class MessageReadStatus(models.Model):
    """
    Track read status of messages for each user
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_read_statuses')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
        
    def __str__(self):
        return f"{self.user.username} read message at {self.read_at}"


class ChatNotification(models.Model):
    """
    Notifications for new messages
    """
    NOTIFICATION_TYPES = [
        ('new_message', 'New Message'),
        ('new_room', 'New Chat Room'),
        ('user_joined', 'User Joined'),
        ('user_left', 'User Left'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_notifications')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='new_message')
    content = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.content}"


class BlockedUser(models.Model):
    """
    Handle user blocking functionality
    """
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    blocked_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ['blocker', 'blocked']
        
    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"