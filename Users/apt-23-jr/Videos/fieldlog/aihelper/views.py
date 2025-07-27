from django.shortcuts import render

# Create your views here.
import openai
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

@csrf_exempt
def ai_recommendation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question')

        if not question:
            return JsonResponse({'error': 'Question is required'}, status=400)

        prompt = f"""You are an expert assistant in university field placements.
        A student asked: "{question}". Recommend suitable placement options."""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful field placement assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            reply = response.choices[0].message['content']
            return JsonResponse({'answer': reply})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
