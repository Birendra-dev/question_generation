from django.shortcuts import render
from .forms import InputForm
from apps.questionGeneration import get_question, question_model, question_tokenizer
from apps.summarization import summarizer, summary_model, summary_tokenizer

def generate_mcq(request):
    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            context = form.cleaned_data['context']
            answer = form.cleaned_data['answer']
            
            # Summarize the context
            summary_text = summarizer(context, summary_model, summary_tokenizer)
            
            # Generate question from the summarized context and answer
            question = get_question(summary_text, answer, question_model, question_tokenizer)
            
            # Pass context, summary, answer, and question to the template
            return render(request, 'quesGens/result.html', {
                'context': context,
                'summary': summary_text,
                'answer': answer,
                'question': question
            })
    else:
        form = InputForm()

    return render(request, 'quesGens/index.html', {'form': form})
