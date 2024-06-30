from django.shortcuts import render
import json
from django.http import HttpResponse,JsonResponse
import google.generativeai as genai
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login
from PyPDF2 import PdfReader
from rest_framework.authtoken.models import Token
from .models import Quiz,User
from django.core import serializers
from django_ratelimit.decorators import ratelimit
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
import os
from dotenv import load_dotenv
load_dotenv()

key=os.environ.get('gemini_key')
genai.configure(api_key=key)
model = genai.GenerativeModel('gemini-1.5-pro-latest')


def process_json_string(input_str):
    try:
        start_index = input_str.find('[')
        end_index = input_str.rfind(']')
        json_str = input_str[start_index:end_index+1]
        python_obj = json.loads(json_str)
        return python_obj
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])  
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='5/1m') 
def text_prompt(req):
    if req.method=='POST':
        try:
            json_data=json.loads(req.body)
            prompt=json_data.get('topic')
            difficulty=json_data.get('difficulty')
            # print(prompt)
            instruction="10 "+ difficulty + " mcqs on " + prompt + ".Format your answer as JSON string with question,unmarked options,answer and explanation"
            print(instruction)
            response = model.generate_content(instruction)
            print(response.text)
            mcq=process_json_string(response.text)
            # print(mcq)
            x = json.dumps(mcq)
            print(x)
            if not mcq:
                return JsonResponse(status=400)
            return JsonResponse({"MCQ":x},status=200)
        except Exception as e:
             print(f"Error processing request: {e}")
             return JsonResponse({'error': 'Internal server error'}, status=500)
    else:
        return JsonResponse({'error':"Incorrect HTTP Method"})

def extractText(fileName):
        reader = PdfReader(fileName)
        text=""
        for i in range(0,len(reader.pages)):
            page = reader.pages[i]
            text=text+page.extract_text()
        return text    

@api_view(['POST'])    
@authentication_classes([TokenAuthentication])  
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='5/1m') 
def pdf_prompt(req):
    if req.FILES.get('pdf'):
        uploaded_file = req.FILES['pdf']
        print(uploaded_file)
        prompt= extractText(uploaded_file)
        
        prompt[:30000]
        instruction="Read the following: "+prompt + " Ask 10 mcqs.Format your answer as JSON string with question,options,answer and explanation"
        print(instruction)
        response = model.generate_content(instruction)
        print(response.text)  
        mcq=process_json_string(response.text)
        x = json.dumps(mcq)
        print(x)
        if not mcq:
            return JsonResponse(status=400)
        return JsonResponse({"MCQ":x},status=200) 
    else:
        return JsonResponse({'error': 'No PDF file uploaded'}, status=400)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])  
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='5/1m') 
def submit_quiz(request):
        try:
            data = json.loads(request.body)
            # print(data)
            user = request.user
            print(user)
            topic = data.get('topic')
            quiz_data = data.get('quiz_data')
            score = data.get('score')
            current_user=User.objects.filter(username=user).first()
            # print(current_user)
            new_quiz,created=Quiz.objects.update_or_create(user=current_user,topic=topic,quiz_data=quiz_data,score=score)
            
           
            return JsonResponse({'message': 'Quiz submitted successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])  
@permission_classes([IsAuthenticated])
def user_history(req):
    try:
        user=req.user
        print(user)
        test_data=Quiz.objects.filter(user=user)
        # print(test_data)
        test_response=[]
        for test in test_data:
            test_info={
                "topic":test.topic,
                "quiz_string":test.quiz_data,
                "marks":test.score,
            }
            test_response.append(test_info)
        print(test_response)    
        return JsonResponse({'data': test_response}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])  
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        token = request.auth
        if token:
            token.delete()
        return JsonResponse(status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@api_view(['POST'])
def register_view(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        token, created = Token.objects.get_or_create(user=user)
        
        return JsonResponse({'message': 'User registered successfully', 'token': token.key}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)    

@api_view(['POST'])
def login_view(req):
     try:
          data=json.loads(req.body)
        #   print(data)
          user=authenticate(req,username=data['username'],password=data['password'])
        #   if user:
          if user:
            token, _ = Token.objects.get_or_create(user=user)
            print(token)
            return JsonResponse({'token': token.key}, status=200)
          else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
               
     except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
     
@api_view(['GET'])
def hello_world(req):
     try:
            return JsonResponse({'MESSAGE': 'HELLO'}, status=200)
               
     except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)     
    


