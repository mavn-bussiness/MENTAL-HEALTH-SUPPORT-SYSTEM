from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Conversation, Message
from accounts.models import User
from django.db.models import Q

# Create your views here.

@login_required
def conversation_list(request):
    conversations = request.user.conversations.all().order_by('-updated_at')
    return render(request, 'messaging/conversation_list.html', {'conversations': conversations})

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in conversation.participants.all():
        messages.error(request, 'Access denied.')
        return redirect('messaging:conversation_list')
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(conversation=conversation, sender=request.user, content=content)
            conversation.updated_at = models.DateTimeField(auto_now=True)
            conversation.save()
            return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    messages_list = conversation.messages.order_by('timestamp')
    return render(request, 'messaging/conversation_detail.html', {'conversation': conversation, 'messages': messages_list})

@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    # Check if user can message this person
    if request.user.role == 'client' and other_user.role != 'therapist':
        messages.error(request, 'Clients can only message therapists.')
        return redirect('messaging:conversation_list')
    elif request.user.role == 'therapist' and other_user.role != 'client':
        messages.error(request, 'Therapists can only message clients.')
        return redirect('messaging:conversation_list')
    # Check if conversation already exists
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    if existing_conversation:
        return redirect('messaging:conversation_detail', conversation_id=existing_conversation.id)
    # Create new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)
