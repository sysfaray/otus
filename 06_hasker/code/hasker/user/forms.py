from django import forms
from user.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'avatar')


class SignupForm(forms.Form):
    class Meta:
        model = User
    login = forms.CharField(label='Login')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password', max_length=200)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Repeat password', max_length=200)
    avatar = forms.ImageField(label='Avatar')


