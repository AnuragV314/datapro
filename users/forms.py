from django import forms
from .models import User

# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password_hash', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
#         widgets = {
#             'password_hash': forms.PasswordInput(),
#         }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["bio", "expertise", "profile_image"]
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 px-4 py-3 transition-all duration-150 ease-in-out placeholder-gray-400 dark:placeholder-gray-500",
                    "rows": 4,
                    "placeholder": "Write something about yourself...",
                }
            ),
            "expertise": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 px-4 py-3 transition-all duration-150 ease-in-out placeholder-gray-400 dark:placeholder-gray-500 ",
                    "placeholder": "e.g. Machine Learning, Web Development, Data Science",
                }
            ),
            "profile_image": forms.ClearableFileInput(
                attrs={"class": "hidden", "id": "image-upload"}
            ),
        }
