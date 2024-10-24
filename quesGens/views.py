import torch
from django.shortcuts import render
from .forms import InputForm
from apps.questionGeneration import get_question, question_model, question_tokenizer
from apps.summarization import summarizer, summary_model, summary_tokenizer
from apps.keywordExtraction import get_keywords
from apps.distractors import get_distractors, s2v
import random


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
                distractors = get_distractors(keyword, s2v)  # Generate distractors for the keyword
                
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