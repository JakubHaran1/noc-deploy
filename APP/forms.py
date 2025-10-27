from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import DateInput
from APP.models import PartyModel,  PartyUser

from django.core.exceptions import ValidationError

from datetime import date


class myDateInput(DateInput):
    input_type = "date"


class PartyForm(forms.ModelForm):
    date = forms.DateField(widget=myDateInput)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}))

    class Meta:
        model = PartyModel
        exclude = ["creation_day", "participants", "author"]

    def clean(self):
        cleaned_data = super().clean()
        age = cleaned_data.get("age")
        alco = cleaned_data.get("alco")

        if age < 18 and alco:
            raise ValidationError("You can't drink alcohol before 18")
        return cleaned_data


class LoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        pass


class RegisterForm(UserCreationForm):
    birth = forms.DateField(widget=myDateInput)
    avatar = forms.FileField(required=False)

    def clean_birth(self):
        clean_birth = self.cleaned_data["birth"]
        today = date.today()

        age = (today.year - clean_birth.year) - ((today.month, today.day)
                                                 < (clean_birth.month, clean_birth.day))
        if (age) < 16:
            raise ValidationError("You have to be older than 16 years old")
        return clean_birth

    def clean_avatar(self):

        avatar = self.cleaned_data["avatar"]
        if not avatar:
            raise ValidationError("You have to pass avatar")
        if not avatar.name.lower().endswith((".jpg", ".png", ".webp")):
            raise ValidationError("Wrong file type!")
        return avatar

    class Meta:
        model = PartyUser
        fields = ("username", "email", "password1",
                  "password2", "birth", "avatar")


class EmailChangeForm(forms.Form):
    email = forms.EmailField(required=True)
