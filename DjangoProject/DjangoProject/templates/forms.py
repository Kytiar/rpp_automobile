from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Category, UserProfile, Author


class PostForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'categories']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and hasattr(self.user, 'profile') and self.user.profile.role in ['admin', 'editor']:
            self.fields['author'] = forms.ModelChoiceField(
                queryset=Author.objects.all(),
                required=True
            )


# blog/forms.py
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, initial='author')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            # Проверяем, существует ли уже профиль
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user, role=self.cleaned_data['role'])
            if not hasattr(user, 'author'):
                Author.objects.create(user=user)

        return user