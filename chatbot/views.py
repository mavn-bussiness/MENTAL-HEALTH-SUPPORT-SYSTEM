from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
from dotenv import load_dotenv
from .models import ChatbotMessage
import os
import google.generativeai as genai
load_dotenv()

def get_bot_response(user_message, action_type=None):
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        return "Sorry, Gemini API key is missing. Please check configuration."

    # Configure the client
    genai.configure(api_key=gemini_api_key)

    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(m.name)

    # Use Gemini's chat model
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Action prompts
    action_prompts = {
        'anxiety_support': "Provide coping strategies for anxiety.",
        'stress_relief': "Share relaxation techniques for stress relief.",
        'mindfulness': "Guide me through a mindfulness meditation practice."
    }

    prompt = action_prompts.get(action_type, user_message)

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Sorry, something went wrong with Gemini: {str(e)}"


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