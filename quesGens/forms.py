from django import forms

class InputForm(forms.Form):
    context = forms.CharField(widget=forms.Textarea, label='Context')
    answer = forms.CharField(max_length=100, label='Answer')  # Add an answer field
