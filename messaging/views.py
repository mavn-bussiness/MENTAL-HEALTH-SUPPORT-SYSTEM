from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Max
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
import json

from .models import ChatRoom, Message, MessageReadStatus, ChatNotification, BlockedUser
from .forms import MessageForm

User = get_user_model()

@login_required
def chat_dashboard(request):
    """
    Main chat dashboard showing all user's chat rooms
    """
    # Get user's chat rooms with latest message info
    chat_rooms = ChatRoom.objects.filter(
        participants=request.user,
        is_active=True
    ).annotate(
        unread_count=Count(
            'messages',
            filter=Q(
                ~Q(messages__sender=request.user),
                ~Q(messages__read_statuses__user=request.user),
                messages__is_deleted=False,
                
            ),
            distinct=True
        ),
        latest_message_time=Max('messages__sent_at')
    ).order_by('-latest_message_time')
    
    # Get available therapists for new chats (if user is client)
    available_therapists = []
    if request.user.role == 'client':
        # Get therapists not blocked and not already in chat with user
        existing_therapy_rooms = ChatRoom.objects.filter(
            participants=request.user,
            room_type='therapy'
        ).values_list('participants__id', flat=True)
        
        blocked_users = BlockedUser.objects.filter(
            Q(blocker=request.user) | Q(blocked=request.user)
        ).values_list('blocked_id', 'blocker_id')
        blocked_user_ids = set()
        for blocked, blocker in blocked_users:
            blocked_user_ids.update([blocked, blocker])
        
        available_therapists = User.objects.filter(
            role='therapist',
            is_active=True
        ).exclude(
            Q(id__in=existing_therapy_rooms) | Q(id__in=blocked_user_ids)
        )[:10]
    
    context = {
        'chat_rooms': chat_rooms,
        'available_therapists': available_therapists,
        'user_role': request.user.role,
    }
    return render(request, 'messaging/chat_dashboard.html', context)


@login_required
def chat_room(request, room_id):
    """
    Individual chat room view
    """
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if user is participant
    if not room.participants.filter(id=request.user.id).exists():
        return HttpResponseForbidden("You don't have access to this chat room.")
    
    # Get messages with pagination
    messages_list = Message.objects.filter(
        room=room,
        is_deleted=False
    ).select_related('sender', 'reply_to__sender').order_by('sent_at')
    
    paginator = Paginator(messages_list, 50)  # 50 messages per page
    page_number = request.GET.get('page', paginator.num_pages)  # Start from last page
    messages_page = paginator.get_page(page_number)
    
    # Mark messages as read
    unread_messages = Message.objects.filter(
        room=room,
        is_deleted=False
    ).exclude(
        Q(sender=request.user) | Q(read_statuses__user=request.user)
    )
    
    for message in unread_messages:
        MessageReadStatus.objects.get_or_create(
            message=message,
            user=request.user
        )
    
    # Get other participant for 1-on-1 chats
    other_participant = None
    if room.room_type == 'therapy':
        other_participant = room.get_other_participant(request.user)
    
    # Check if user is blocked
    is_blocked = False
    if other_participant:
        is_blocked = BlockedUser.objects.filter(
            Q(blocker=request.user, blocked=other_participant) |
            Q(blocker=other_participant, blocked=request.user)
        ).exists()
    
    context = {
        'room': room,
        'messages': messages_page,
        'other_participant': other_participant,
        'is_blocked': is_blocked,
        'can_send_files': request.user.role in ['therapist', 'admin'],
        'room_id_str': str(room.id),  # For WebSocket connection
    }
    
    return render(request, 'messaging/chat_room.html', context)


@login_required
@require_http_methods(["POST"])
def send_message(request, room_id):
    """
    Send a message via AJAX
    """
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check permissions
    if not room.participants.filter(id=request.user.id).exists():
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Check if user is blocked
    if room.room_type == 'therapy':
        other_participant = room.get_other_participant(request.user)
        if other_participant and BlockedUser.objects.filter(
            Q(blocker=request.user, blocked=other_participant) |
            Q(blocker=other_participant, blocked=request.user)
        ).exists():
            return JsonResponse({'error': 'Cannot send message - user blocked'}, status=403)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        reply_to_id = data.get('reply_to')
        
        if not content:
            return JsonResponse({'error': 'Message content is required'}, status=400)
        
        # Create message
        message = Message.objects.create(
            room=room,
            sender=request.user,
            content=content,
            reply_to_id=reply_to_id if reply_to_id else None
        )
        
        # Create notifications for other participants
        for participant in room.participants.exclude(id=request.user.id):
            ChatNotification.objects.create(
                recipient=participant,
                room=room,
                message=message,
                notification_type='new_message',
                content=f"New message from {request.user.first_name or request.user.username}"
            )
        
        # Return message data
        return JsonResponse({
            'success': True,
            'message': {
                'id': str(message.id),
                'content': message.content,
                'sender': {
                    'username': message.sender.username,
                    'first_name': message.sender.first_name,
                    'role': message.sender.role,
                },
                'sent_at': message.sent_at.strftime('%H:%M'),
                'is_own': True,
                'reply_to': {
                    'content': message.reply_to.content[:50] if message.reply_to else None,
                    'sender': message.reply_to.sender.username if message.reply_to else None
                } if message.reply_to else None
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Failed to send message'}, status=500)


@login_required
def start_chat(request, user_id):
    """
    Start a new chat with a therapist/client
    """
    other_user = get_object_or_404(User, id=user_id)
    
    # Validation rules
    if request.user.role == 'client' and other_user.role != 'therapist':
        messages.error(request, "Clients can only chat with therapists.")
        return redirect('messaging:chat_dashboard')
    
    if request.user.role == 'therapist' and other_user.role not in ['client', 'therapist']:
        messages.error(request, "Invalid chat recipient.")
        return redirect('messaging:chat_dashboard')
    
    # Check if chat already exists
    existing_room = ChatRoom.objects.filter(
        participants=request.user,
        room_type='therapy'
    ).filter(participants=other_user).first()
    
    if existing_room:
        return redirect('messaging:chat_room', room_id=existing_room.id)
    
    # Create new chat room
    room = ChatRoom.objects.create(
        room_type='therapy',
        name=f"Therapy Chat: {request.user.username} & {other_user.username}"
    )
    room.participants.add(request.user, other_user)
    
    # Send initial system message
    Message.objects.create(
        room=room,
        sender=request.user,  # System message from initiator
        content=f"Chat session started between {request.user.first_name or request.user.username} and {other_user.first_name or other_user.username}",
        message_type='system'
    )
    
    # Notify other user
    ChatNotification.objects.create(
        recipient=other_user,
        room=room,
        notification_type='new_room',
        content=f"{request.user.first_name or request.user.username} started a chat with you"
    )
    
    messages.success(request, f"Chat started with {other_user.first_name or other_user.username}")
    return redirect('messaging:chat_room', room_id=room.id)


@login_required
def load_messages(request, room_id):
    """
    Load older messages for infinite scroll
    """
    room = get_object_or_404(ChatRoom, id=room_id)
    
    if not room.participants.filter(id=request.user.id).exists():
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    before_id = request.GET.get('before')
    
    messages_query = Message.objects.filter(
        room=room,
        is_deleted=False
    ).select_related('sender', 'reply_to__sender')
    
    if before_id:
        messages_query = messages_query.filter(sent_at__lt=Message.objects.get(id=before_id).sent_at)
    
    messages_list = messages_query.order_by('-sent_at')[:20]  # Get 20 older messages
    messages_list = reversed(messages_list)  # Reverse to chronological order
    
    messages_data = []
    for message in messages_list:
        messages_data.append({
            'id': str(message.id),
            'content': message.content,
            'sender': {
                'username': message.sender.username,
                'first_name': message.sender.first_name,
                'role': message.sender.role,
            },
            'sent_at': message.sent_at.strftime('%H:%M'),
            'is_own': message.sender == request.user,
            'message_type': message.message_type,
            'reply_to': {
                'content': message.reply_to.content[:50] if message.reply_to else None,
                'sender': message.reply_to.sender.username if message.reply_to else None
            } if message.reply_to else None
        })
    
    return JsonResponse({
        'messages': messages_data,
        'has_more': messages_query.count() > 20
    })


@login_required
@require_http_methods(["POST"])
def block_user(request, user_id):
    """
    Block/unblock a user
    """
    user_to_block = get_object_or_404(User, id=user_id)
    
    if user_to_block == request.user:
        return JsonResponse({'error': 'Cannot block yourself'}, status=400)
    
    blocked_relation, created = BlockedUser.objects.get_or_create(
        blocker=request.user,
        blocked=user_to_block
    )
    
    if not created:
        # Unblock
        blocked_relation.delete()
        return JsonResponse({'success': True, 'action': 'unblocked'})
    else:
        return JsonResponse({'success': True, 'action': 'blocked'})


@login_required
def notifications(request):
    """
    Get unread notifications
    """
    notifications = ChatNotification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:10]
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'content': notification.content,
            'room_id': str(notification.room.id),
            'created_at': notification.created_at.strftime('%H:%M'),
            'type': notification.notification_type
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': notifications.count()
    })


@login_required
@require_http_methods(["POST"])
def mark_notifications_read(request):
    """
    Mark notifications as read
    """
    ChatNotification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    return JsonResponse({'success': True})