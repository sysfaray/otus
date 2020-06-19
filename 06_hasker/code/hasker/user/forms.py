from django import forms
from user.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email','avatar',)


class SignupForm(forms.Form):
    class Meta:
        model = User

    login = forms.CharField(label='Login', max_length=200)
    email = forms.EmailField(label='Email', max_length=200)
    password = forms.CharField(widget=forms.PasswordInput, label='Password', max_length=200)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Repeat password', max_length=200)
    avatar = forms.ImageField(label='Avatar')

    def clean_login(self):
        login = self.cleaned_data['login']
        if User.objects.filter(username=login).exists():
            raise forms.ValidationError('User with login "' + login+ '" already exists')
        return login

