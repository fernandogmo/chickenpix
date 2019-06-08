from django import forms

class EmailForm(forms.Form):
    email = forms.EmailField(max_length=256)

class TokenForm(forms.Form):
    token = forms.CharField(max_length=6)
