from django import forms


class InputForm(forms.Form):
    context = forms.CharField(widget=forms.Textarea, label="Context")
    num_keywords = forms.IntegerField(
        label="Number of Keywords",
        min_value=1,
        initial=4,  # Default value, can be changed
        help_text="Select how many keywords to use for generating MCQs",
    )
