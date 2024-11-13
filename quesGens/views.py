from django.http import JsonResponse
import torch
from django.shortcuts import render,redirect
from .forms import InputForm
from apps.questionGeneration import get_question, question_model, question_tokenizer
from apps.summarization import summarizer, summary_model, summary_tokenizer
from apps.keywordExtraction import get_keywords
from apps.distractors import get_distractors
from django.contrib.auth.models import User
# django bydefault give user models.if we dont want to add additional feilds it is better to use it
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
import random

# these are the code committed for ease
# def generate_mcq(request):
#     # Dummy data for MCQs
#     mcq_list = [
#         {
#             'question': 'What is the capital of France?',
#             'options': ['Berlin', 'Madrid', 'Paris', 'Rome'],
#             'correct_answer': 'Paris'
#         },
#         {
#             'question': 'Which planet is known as the Red Planet?',
#             'options': ['Earth', 'Mars', 'Jupiter', 'Saturn'],
#             'correct_answer': 'Mars'
#         },
#         {
#             'question': 'What is the largest ocean on Earth?',
#             'options': ['Atlantic Ocean', 'Indian Ocean', 'Arctic Ocean', 'Pacific Ocean'],
#             'correct_answer': 'Pacific Ocean'
#         },
#     ]

#     # Prepare data to be sent to the result template
#     result_data = {
#         'mcq_list': mcq_list  # List of dummy questions with options
#     }

#     return render(request, 'quesGens/result.html', result_data)
# def generate_mcq(request):
#     try:
#         # Initialize sense2vec with optimized memory settings
#         # from sense2vec import Sense2Vec
#         # s2v = Sense2Vec().from_disk('path_to_your_s2v_model')
        
#         # Get your words list
#         words = [...] # Your list of words
        
#         # Process in batches
#         distractors = batch_process_distractors(words, s2v)
        
#         return JsonResponse({'success': True, 'data': distractors})
        
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})

def generate_mcq(request):
    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            context = form.cleaned_data['context']
            #option to select the number of keywords
            num_keywords = int(form.cleaned_data['num_keywords'])

            # Step 1: Summarize the context
            summary_text = summarizer(context, summary_model, summary_tokenizer)

            # Step 2: Extract keywords from original context and summarized text
            keywords = get_keywords(context, summary_text, num_keywords)

            distractors_dict = {}
            questions_dict = {}  # Store questions for each keyword

            # Step 3: Generate questions and distractors
            for keyword in keywords:
                question = get_question(summary_text, keyword, question_model, question_tokenizer)  # Generate question based on the summary
                # distractors = get_distractors(keyword, s2v)  # Generate distractors for the keyword
                distractors = get_distractors(keyword) 
                # try:
                #         # Initialize sense2vec with optimized memory settings
                #         # from sense2vec import Sense2Vec
                #         # s2v = Sense2Vec().from_disk('path_to_your_s2v_model')
                        
                #         # Get your words list
                #         words = [...] # Your list of words
                        
                #         # Process in batches
                #         distractors = batch_process_distractors(keyword, s2v)
                #         questions_dict[keyword] = question
                #         distractors_dict[keyword] = distractors
                #         return JsonResponse({'success': True, 'data': distractors})
                        
                # except Exception as e:
                #         return JsonResponse({'success': False, 'error': str(e)})
                # distractors= get_distractors(keyword,glove_model)
                # Store the question and distractors for the keyword
                questions_dict[keyword] = question
                distractors_dict[keyword] = distractors

            # Step 4: Prepare MCQs in the correct format
            mcq_list = []
            for keyword in keywords:
                question = questions_dict[keyword]
                correct_answer = keyword
                distractors = distractors_dict[keyword]
                
                # Combine correct answer with distractors and shuffle them
                options = [correct_answer] + distractors
                random.shuffle(options)
                
                # Append the MCQ to the list
                mcq_list.append({
                    'question': question,
                    'options': options,
                    'correct_answer': correct_answer  # For verification purposes if needed
                })

            # Step 5: Prepare data to be sent to the result template
            result_data = {
                'context': context,
                'summary_text': summary_text,
                'mcq_list': mcq_list  # List of questions with options
            }

            return render(request, 'quesGens/result.html', result_data)

    else:
        form = InputForm()

    return render(request, 'quesGens/index.html', {'form': form})





# def register(request):
#     if request.method=='POST':
#          username=request.POST.get('username')
#          password=request.POST.get('password')
#          if User.objects.filter(username=username).exists():
#               messages.error(request,'username already exists')
#          else:
#              user=User.objects.create_user(username=username,password=password)
#              user.save()
#              login(request,user)
#              messages.success(request,"you are registered successfully!")
#              return redirect('login')
#     return render(request,'register.html')
def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            return JsonResponse({'success': False, 'message': 'Passwords do not match'})
        
        if User.objects.filter(username=email).exists():
            return JsonResponse({'success': False, 'message': 'Email already in use'})
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
        login(request, user)
        return JsonResponse({'success': True, 'message': 'Registration successful'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful")  # Optional: feedback message
            next_url = request.POST.get('next','result')  #re Use 'next' parameter to redirect
            return redirect(next_url)
            # return JsonResponse({'success': True, 'message': 'Login successful'})
            # messages.success(request,"login successful")
        else:
            messages.error(request, 'Invalid credentials')  # Feedback for invalid login
            return redirect('login')
            # return JsonResponse({'success': False, 'message': 'Invalid credentials'})
            # messages.success(request,'incorrect')

    return JsonResponse({'success': False, 'message': 'Invalid request'})
    messages.success(request,'invalid')
# we can also use django form for simplicity.

def is_logged_in(request):
    return JsonResponse({'logged_in': request.user.is_authenticated})
# quesGens/views.py

# from django.http import HttpResponseForbidden

# def csrf_failure_view(request, reason=""):
#     return HttpResponseForbidden("CSRF verification failed. Please try again.")






