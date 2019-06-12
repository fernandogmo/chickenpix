from django import forms


class EmailForm(forms.Form):
    email = forms.EmailField(max_length=256,
                             label='',
                             widget=forms.EmailInput(
                                 attrs={
                                     'class': 'form-control',
                                     'placeholder': 'Email address',
                                     'autofocus': True,
                                     }))


class TokenForm(forms.Form):
    token = forms.CharField(max_length=6,
                            label='',
                            widget=forms.TextInput(
                                attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Token',
                                    'autofocus': True,
                                    }))
