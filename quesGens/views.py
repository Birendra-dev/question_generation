import random

from django.shortcuts import render
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

from apps.s2vdistractors import get_distractors, s2v
from apps.summarization import summarizer, summary_model, summary_tokenizer
from apps.keywordExtraction import get_keywords
from apps.questionGeneration import get_question, question_model, question_tokenizer


from apps.rakeKeyword import get_keywords_rake
from apps.t5distractors import get_distractors_t5, dis_model, dis_tokenizer
from apps.distilBERTKeyword import extract_keywords
from .forms import InputForm


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
                mcq_list.append(
                    {
                        "question": question,
                        "options": options,
                        "correct_answer": correct_answer,  # For verification purposes if needed
                    }
                )

            # Save mcq_list in the session
            request.session['mcq_list'] = mcq_list

            # Prepare data to be passed to the template
            result_data = {
                "context": context,
                # "summary_text": summary_text,
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
