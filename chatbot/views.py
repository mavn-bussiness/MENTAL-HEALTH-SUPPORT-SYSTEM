from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ChatbotMessage
import os
import openai
import openai.error

# Placeholder for OpenAI or other LLM integration
def get_bot_response(user_message):
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        return "Sorry, the assistant is currently unavailable due to missing API credentials. Please contact support."
    openai.api_key = openai_api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful mental health assistant. Only respond in English. Provide information about mental health, its domains, and answer questions knowledgeably."},
                {"role": "user", "content": user_message},
            ]
        )
        bot_message = response['choices'][0]['message']['content']
        return bot_message
    except openai.error.RateLimitError:
        return "Sorry, the assistant is currently busy due to high demand. Please try again in a few moments."
    except openai.error.AuthenticationError:
        return "Sorry, the assistant is currently unavailable due to invalid API credentials. Please contact support."
    except openai.error.APIConnectionError:
        return "Sorry, the assistant cannot connect to the server right now. Please check your internet connection or try again later."
    except openai.error.OpenAIError as e:
        return f"Sorry, there was an error contacting the assistant: {str(e)}. Please try again later."
    except Exception:
        return "Sorry, an unexpected error occurred. Please try again later."


def chatbot_dashboard(request):
    chat_history = []
    if request.user.is_authenticated:
        chat_history = ChatbotMessage.objects.filter(user=request.user).order_by('timestamp')
    return render(request, 'chatbot/dashboard.html', {'chat_history': chat_history})

@csrf_exempt  # For demonstration; in production, use proper CSRF handling
def chatbot_response(request):
    if request.method == 'POST':
        user = request.user if request.user.is_authenticated else None
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_message = data.get('message', '')
        except Exception:
            user_message = request.POST.get('message', '')
        bot_message = get_bot_response(user_message)
        # Save user and bot messages if user is authenticated
        if user:
            ChatbotMessage.objects.create(user=user, message=user_message, is_bot=False)
            ChatbotMessage.objects.create(user=user, message=bot_message, is_bot=True)
        return JsonResponse({'message': bot_message})
    return JsonResponse({'message': 'Invalid request.'})
