import torch
from django.shortcuts import render
from .forms import InputForm
from apps.questionGeneration import get_question, question_model, question_tokenizer
from apps.summarization import summarizer, summary_model, summary_tokenizer
from apps.keywordExtraction import get_keywords
from apps.distractors import get_distractors, s2v


def generate_mcq(request):
    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            context = form.cleaned_data['context']
            answer = form.cleaned_data['answer']

            # Step 1: Summarize the context
            summary_text = summarizer(context, summary_model, summary_tokenizer)
            
            # Step 2: Generate question from summary and answer
            question = get_question(summary_text, answer, question_model, question_tokenizer)

            # Step 3: Extract keywords from original context and summarized text
            keywords = get_keywords(context, summary_text)

            # Step 4: Generate distractors for each keyword
            distractors_dict = {}
            for keyword in keywords:
                distractors = get_distractors(keyword, s2v)
                distractors_dict[keyword] = distractors


            # Prepare data to be sent to the result template
            result_data = {
                'context': context,
                'summary_text': summary_text,
                'question': question,
                'answer': answer,
                'keywords': keywords,
                'distractors_dict': distractors_dict  # Include distractors in the context
            }

            return render(request, 'quesGens/result.html', result_data)
    else:
        form = InputForm()

    return render(request, 'quesGens/index.html', {'form': form})