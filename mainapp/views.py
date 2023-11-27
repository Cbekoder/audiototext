from django.shortcuts import render
import requests
from django.views import View
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Audio
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST' and request.POST.get('forma')=='f2':
        user = authenticate(
            username = request.POST.get('l'),
            password = request.POST.get('p')
        )
        if user is None:
            return redirect("/login/")
        login(request, user)
        return redirect('/')
    elif request.method == 'POST' and request.POST.get('forma')=='f1':
        try:
            User.objects.create_user(
                username=request.POST.get('username'),
                email=request.POST.get('email'),
                password=request.POST.get('password')
            )
        finally:
            return redirect('/login/')
    return render(request, 'reg.html')

def logout_view(request):
    logout(request)
    return redirect('/')

class AudioView(View):
    def get(self, request):
        if request.user.is_authenticated:
            content = {
                'history' : Audio.objects.filter(userid = request.user).order_by('-id')
            }
            return render(request, 'index.html', content)
        return redirect("/login/")

    def post(self, request):
        if request.user.is_authenticated:

            if request.POST.get('forma') == 'f1':
                audio_file = request.FILES['audio_file']
            elif request.POST.get('forma')=='f2':
                audio_file = request.FILES.get('audio')
            # api_key = 'fdfdd434-d03e-45c8-9f65-e0defaaa1e23:2b689c06-2feb-4f8e-b7fc-d768df7c6763'
            url = 'https://studio.mohir.ai/api/v1/stt'
            payload = {}
            files = [
                ('file', ('out.wav', audio_file, 'audio/wav'))
            ]
            headers = {
                'Authorization': 'fdfdd434-d03e-45c8-9f65-e0defaaa1e23:2b689c06-2feb-4f8e-b7fc-d768df7c6763'
            }

            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            if response.status_code == 200:
                response_data = response.json()
                transcribed_text = response_data.get('result', '')
                print(transcribed_text)
                Audio.objects.create(
                    audiofile = audio_file,
                    txt = transcribed_text["text"],
                    userid = request.user
                )
                return render(request, 'index.html', {'history' : Audio.objects.filter(userid = request.user).order_by('-id'), 'transcribed_text': transcribed_text["text"]})
            else:
                return HttpResponse('Error transcribing audio', status=response.status_code)
            return redirect('/')
        return redirect("/login/")



def transcibe(file):
    # api_key = 'fdfdd434-d03e-45c8-9f65-e0defaaa1e23:2b689c06-2feb-4f8e-b7fc-d768df7c6763'
    url = 'https://studio.mohir.ai/api/v1/stt'
    payload = {}
    files = [
        ('file', ('out.wav', file, 'audio/wav'))
    ]
    headers = {
        'Authorization': 'fdfdd434-d03e-45c8-9f65-e0defaaa1e23:2b689c06-2feb-4f8e-b7fc-d768df7c6763'
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    if response.status_code == 200:
        response_data = response.json()
        transcribed_text = response_data['result']
        print(transcribed_text)
        return transcribed_text
    else:
        return HttpResponse('Error transcribing audio')