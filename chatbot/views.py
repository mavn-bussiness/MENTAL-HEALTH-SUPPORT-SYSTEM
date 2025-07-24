from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
from .models import ChatbotMessage
import os
from openai import OpenAI
from openai import OpenAIError

def get_bot_response(user_message, action_type=None):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        return "Sorry, the assistant is currently unavailable due to missing API credentials. Please contact support."
    
    client = OpenAI(api_key=openai_api_key)
    
    # Map quick action buttons to specific prompts
    action_prompts = {
        'anxiety_support': "Provide coping strategies for anxiety.",
        'stress_relief': "Share relaxation techniques for stress relief.",
        'mindfulness': "Guide me through a mindfulness meditation practice."
    }
    
    # Use action-specific prompt if provided, else use user message
    prompt = action_prompts.get(action_type, user_message)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful mental health assistant. Only respond in English. Provide information about mental health, its domains, and answer questions knowledgeably."},
                {"role": "user", "content": prompt},
            ]
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        if "rate_limit" in str(e):
            return "Sorry, the assistant is busy due to high demand. Please try again later."
        elif "authentication" in str(e):
            return "Sorry, the assistant is unavailable due to invalid API credentials. Contact support."
        elif "connection" in str(e):
            return "Sorry, the assistant cannot connect to the server. Check your internet or try again later."
        elif "model" in str(e):
            return "Sorry, the requested model is unavailable. Please try again later."
        else:
            return f"Sorry, an error occurred: {str(e)}. Please try again later."
    except Exception:
        return "Sorry, an unexpected error occurred. Please try again later."
    
    from openai import OpenAI



@login_required
def chatbot_dashboard(request):
    chat_history = ChatbotMessage.objects.filter(user=request.user).order_by('timestamp')[:50]  # Limit to 50 messages
    quick_actions = [
        {'name': 'Anxiety Support', 'action_type': 'anxiety_support'},
        {'name': 'Stress Relief', 'action_type': 'stress_relief'},
        {'name': 'Mindfulness', 'action_type': 'mindfulness'}
    ]
    return render(request, 'chatbot/chat.html', {
        'chat_history': chat_history,
        'quick_actions': quick_actions
    })

@ensure_csrf_cookie
def chatbot_response(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    
    user = request.user if request.user.is_authenticated else None
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '').strip()
        action_type = data.get('action_type')  # For quick action buttons
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request data.'}, status=400)
    
    # Validate message length
    if len(user_message) > 500:
        return JsonResponse({'error': 'Message exceeds 500 characters.'}, status=400)
    if not user_message and not action_type:
        return JsonResponse({'error': 'Message or action required.'}, status=400)
    
    # Get bot response
    bot_message = get_bot_response(user_message, action_type)
    
    # Save messages if user is authenticated
    if user:
        if user_message:  # Save user message only if provided (not for quick actions)
            ChatbotMessage.objects.create(user=user, message=user_message, is_bot=False)
        ChatbotMessage.objects.create(user=user, message=bot_message, is_bot=True)
    
    return JsonResponse({
        'message': bot_message,
        'timestamp': timezone.now().strftime('%b %d, %H:%M')
    })