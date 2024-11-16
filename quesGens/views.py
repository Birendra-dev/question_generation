import random
from datetime import datetime
from django.shortcuts import render
from django.http import FileResponse,JsonResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import json
import ast
from django.urls import reverse
from django.shortcuts import render,redirect,get_object_or_404
from apps.s2vdistractors import get_distractors, s2v
from apps.summarization import summarizer, summary_model, summary_tokenizer
from apps.keywordExtraction import get_keywords
from apps.questionGeneration import get_question, question_model, question_tokenizer
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
import random
from apps.rakeKeyword import get_keywords_rake
from apps.t5distractors import get_distractors_t5, dis_model, dis_tokenizer
from apps.distilBERTKeyword import extract_keywords
from .forms import InputForm,UserUpdateForm,ProfileUpdateForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import MCQ
import uuid
def generate_mcq(request):
    if request.method == "POST":
        form = InputForm(request.POST)
        if form.is_valid():
            context = form.cleaned_data["context"]
            # option to select the number of keywords
            num_keywords = int(form.cleaned_data["num_keywords"])
            option_1 = form.cleaned_data["option_1"]  # Question generation choice
            option_2 = form.cleaned_data["option_2"]  # Keyword extraction choice
            option_3 = form.cleaned_data["option_3"]  # Distractor generation choice            
            
            # Step 1: Extract keywords based on the selected option
            if option_2 == 'spacy':
                summary_text = summarizer(context, summary_model, summary_tokenizer)
                keywords = get_keywords(context, summary_text, num_keywords)
            elif option_2 == 'rake':
                keywords = get_keywords_rake(context, num_keywords)
            elif option_2 == 'distilBERT':
                keywords = extract_keywords(context, num_keywords=num_keywords)
            else:
                keywords = []  # Fallback if no valid option selected

            distractors_dict = {}
            questions_dict = {}  # Store questions for each keyword

            # Step 2: Generate questions and distractors
            for keyword in keywords:
                question = get_question(context, keyword, question_model, question_tokenizer)

                # Generate distractors based on the selected option
                if option_3 == 's2v':
                    distractors = get_distractors(keyword, s2v)
                elif option_3 == 't5-llm':
                    distractors = get_distractors_t5(
                        question=question,
                        answer=keyword,
                        context=context,
                        model=dis_model,
                        tokenizer=dis_tokenizer
                    )
                else:
                    distractors = []  # Fallback if no valid option selected

                # Store the question and distractors for the keyword
                questions_dict[keyword] = question
                distractors_dict[keyword] = distractors
           
            
            mcq_list = []
            for keyword in keywords:
                question = questions_dict[keyword]
                correct_answer = keyword
                distractors = distractors_dict[keyword]

                # Combine correct answer with distractors and shuffle them
                options = [correct_answer] + distractors
                while len(options) < 4:
                  options.append("Placeholder") 
                random.shuffle(options)
            #     mcq = MCQ(
            # question=question,
            # correct_answer=correct_answer,
            # option_1=options[0],
            # option_2=options[1],
            # option_3=options[2],
            # option_4=options[3]
            #     )
            #     mcq.save()  # Save the MCQ to the database
                # Append the MCQ to the list
                mcq_list.append(
                    {
                        "question": question,
                        "options": options,
                        "correct_answer": correct_answer,  # For verification purposes if needed
                    }
                )
                

# Assuming `mcq_list` is your list of generated MCQs
            MCQ.objects.create(user=request.user, mcqs=json.dumps(mcq_list))
            result_data = {
                "context": context,
                "mcq_list": mcq_list,  # List of questions with options
            }

            return render(request, "quesGens/result.html", result_data)
    else:
        form = InputForm()

    return render(request, "quesGens/index.html", {"form": form})
def result(request):
    latest_batch = MCQ.objects.latest('created_at') #quering latest generated mcqs from database.
    mcq_list = json.loads(latest_batch.mcqs)
    mcq_list=ast.literal_eval(mcq_list)  #converting to python list
    result_data={
        "mcq_list":mcq_list
    }
    return render(request,'quesGens/result.html',result_data)

@csrf_exempt
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
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        print(f'CSRF token: {request.COOKIES.get("csrftoken")}')

        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
           
            return JsonResponse({'success': True, 'message': 'Login successful'})
           
        else:
           
            return JsonResponse({'success': False, 'message': 'Invalid credentials'})
              
    return JsonResponse({'success': False, 'message': 'Invalid request'})
      
def is_logged_in(request):
    return JsonResponse({'logged_in': request.user.is_authenticated})
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('generate_mcq')  # Redirect after logout
    return redirect('generate_mcq') 


def download_pdf(request):
    mcq_list = request.session.get('mcq_list')
    
    # Check if mcq_list is available
    if not mcq_list:
        return render(request, "quesGens/error.html", {"error": "No MCQs found to download as PDF."})

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y_position = height - 50
    for mcq in mcq_list:
        p.drawString(100, y_position, f"Question: {mcq['question']}")
        y_position -= 20
        for option in mcq['options']:
            p.drawString(120, y_position, f"- {option}")
            y_position -= 15
        y_position -= 30

    p.showPage()
    p.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename="mcqs.pdf")

   
@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                    request.FILES,
                                    instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated! You are able to login')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        context ={
        'u_form':u_form,
        'p_form':p_form
         }
    return render(request,'quesGens/profile.html',context)

def test(request):

    latest_batch = MCQ.objects.latest('created_at')
    print("Type of mcqs:", type(latest_batch.mcqs))

    
    mcq_list = json.loads(latest_batch.mcqs)
    print("Parsed mcq_list:", mcq_list)  # Debugging: print the parsed data
    print(type(mcq_list))
  
    mcq_list=ast.literal_eval(mcq_list)  #converts json string to list
    print(type(mcq_list))
    if request.method == 'POST':
        score = 0
        for i, mcq in enumerate(mcq_list):
            selected_option = request.POST.get(f'option_{i}')
            correct_answer = mcq["correct_answer"]  # Assume each MCQ has a correct_answer field
            if selected_option == correct_answer:
                score += 1
        return render(request, 'quesGens/test_results.html', {'score': score, 'total': len(mcq_list)})

    return render(request, 'quesGens/test.html', {'mc_list': mcq_list})
@login_required
def history(request):
    # Fetch all MCQ entries for the logged-in user
    mcq_entries = MCQ.objects.filter(user=request.user).order_by('-created_at')
    print(mcq_entries)
    # Convert JSON field data into Python objects
    history_data = []
    for entry in mcq_entries:
        mcqs = json.loads(entry.mcqs)  # Convert JSON string back to Python data
        mcqs=ast.literal_eval(mcqs)
        history_data.append({
            "id": entry.id,
            "mcqs": mcqs,
            "created_at": entry.created_at,
        })
    print(history_data)
    # Pass the history data to the template
    return render(request, "quesGens/history.html", {"history_data": history_data})
@login_required
def delete_history(request, entry_id):
    # Get the MCQ entry for the logged-in user
    mcq_entry = get_object_or_404(MCQ, id=entry_id, user=request.user)
    
    # Delete the entry
    mcq_entry.delete()
    
    # Redirect to the history page
    return redirect('history')