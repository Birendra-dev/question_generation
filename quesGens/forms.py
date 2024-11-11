from django import forms


CHOICES_QA = [
    ('general', 'General'),
    ('science', 'Science'),
]
CHOICES_Key = [
    ('rake', 'Rake'),
    ('spacy', 'Spacy'),
    ('distilbert', 'LLM DistilBERT'),  # lowercase to match view logic
]
CHOICES_Distractors = [
    ('s2v', 'Sense2Vec'),
    ('t5-llm', 'LLM T5'),
]

class InputForm(forms.Form):
    context = forms.CharField(widget=forms.Textarea, label="Context")
    num_keywords = forms.IntegerField(
        label="Number of Keywords",
        min_value=1,
        initial=4,  # Default value, can be changed
        help_text="Select how many keywords to use for generating MCQs",
    )
    option_1 = forms.ChoiceField(
        widget=forms.RadioSelect, 
        choices=CHOICES_QA, 
        label="Select an option for Question Generation",
        help_text="Select the type of questions to generate"
    )
    option_2 = forms.ChoiceField(
        widget=forms.RadioSelect, 
        choices=CHOICES_Key, 
        label="Select an option for keyword extraction",
        help_text="Select the method to extract keywords from the context"
    )
    option_3 = forms.ChoiceField(
        widget=forms.RadioSelect, 
        choices=CHOICES_Distractors, 
        label="Select an option for distractors generation",
        help_text="Select the method to generate distractors for the MCQs"
    )

    def __init__(self, *args, **kwargs):
        super(InputForm, self).__init__(*args, **kwargs)
        self.fields['option_1'].initial = 'general'  # Match the key in CHOICES_Key
        self.fields['option_2'].initial = 'rake'   # Match the key in CHOICES_Distractors
        self.fields['option_3'].initial = 's2v'
