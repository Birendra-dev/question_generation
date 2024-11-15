import random
from io import BytesIO

from django.http import FileResponse
from django.shortcuts import render
from .forms import InputForm

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_mcq(request):
    if request.method == "POST":
        form = InputForm(request.POST)
        if form.is_valid():
            context = form.cleaned_data["context"]
            num_keywords = int(form.cleaned_data["num_keywords"])
            option_1 = form.cleaned_data["option_1"]  # Question generation choice
            option_2 = form.cleaned_data["option_2"]  # Keyword extraction choice
            option_3 = form.cleaned_data["option_3"]  # Distractor generation choice
            
            # Extract keywords based on the selected option
            keywords = extract_keywords_based_on_option(option_2, context, num_keywords)

            # Generate questions and distractors
            questions_dict, distractors_dict = generate_questions_and_distractors(
                option_1, option_3, context, keywords
            )

            # Prepare MCQs
            mcq_list = create_mcq_list(keywords, questions_dict, distractors_dict)

            # Store MCQs in session
            request.session['mcq_list'] = mcq_list

            result_data = {
                "context": context,
                "mcq_list": mcq_list,  # List of questions with options
            }

            return render(request, "quesGens/result.html", result_data)

    else:
        form = InputForm()

    return render(request, "quesGens/index.html", {"form": form})


def download_pdf(request):
    mcq_list = request.session.get('mcq_list')
    
    # Check if mcq_list is available
    if not mcq_list:
        return render(request, "quesGens/error.html", 
                      {"error": "No MCQs found to download as PDF."})

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


# Utility Functions

def extract_keywords_based_on_option(option, context, num_keywords):
    """Extract keywords based on the selected option."""
    if option == 'spacy':
        from apps.summarization import summarizer, summary_model, summary_tokenizer
        from apps.keywordExtraction import get_keywords
        
        summary_text = summarizer(context, summary_model, summary_tokenizer)
        return get_keywords(context, summary_text, num_keywords)
    
    elif option == 'rake':
        from apps.rakeKeyword import get_keywords_rake
        return get_keywords_rake(context, num_keywords)
    
    elif option == 'distilBERT':
        from apps.distilBERTKeyword import extract_keywords
        return extract_keywords(context, num_keywords=num_keywords)
    
    return []


def generate_questions_and_distractors(option_1, option_3, context, keywords):
    """Generate questions and distractors for given keywords."""
    questions_dict = {}
    distractors_dict = {}

    # Lazy load models for question generation and distractor generation
    if option_1 == "t5-llm":
        from apps.questionGeneration import get_question, question_model, question_tokenizer
    if option_3 == "t5-llm":
        from apps.t5distractors import dis_model, dis_tokenizer, get_distractors_t5
    if option_3 == "llama":
        from apps.llama_distractors import generate_distractors_llama
    if option_3 == "s2v":
        from apps.s2vdistractors import generate_distractors, s2v

    for keyword in keywords:
        # Generate question
        if option_1 == "t5-llm":
            question = get_question(context, keyword, question_model, question_tokenizer)
        else:
            question = f"What is {keyword}?"  # Fallback question

        # Generate distractors
        if option_3 == "t5-llm":
            distractors = get_distractors_t5(
                question=question,
                answer=keyword,
                context=context,
                model=dis_model,
                tokenizer=dis_tokenizer
            )
        elif option_3 == "llama":
            distractors = generate_distractors_llama(context, question, keyword)
        elif option_3 == "s2v":
            distractors = generate_distractors(keyword, s2v)
        else:
            distractors = []

        questions_dict[keyword] = question
        distractors_dict[keyword] = distractors

    return questions_dict, distractors_dict


def create_mcq_list(keywords, questions_dict, distractors_dict):
    """Combine questions and distractors into MCQ format."""
    mcq_list = []
    for keyword in keywords:
        question = questions_dict[keyword]
        correct_answer = keyword
        distractors = distractors_dict[keyword]

        # Combine correct answer with distractors and shuffle them
        options = [correct_answer] + distractors
        random.shuffle(options)

        mcq_list.append(
            {
                "question": question,
                "options": options,
                "correct_answer": correct_answer,
            }
        )
    return mcq_list
