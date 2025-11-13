
from django.conf import settings

from django import views
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.decorators import login_required


from .forms import PartyForm,  RegisterForm
from .models import PartyModel,  PartyUser
from .tokens import emailActivationToken


from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.core.serializers import serialize

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string


from django.contrib import messages


import os
from datetime import date
import json
import requests
import resend

# Helping functions


def calcAge(birth_year, birth_month, birth_day):
    today = date.today()
    age = (today.year - birth_year) - \
        ((birth_month, birth_day) < (today.month, today.day))
    return age


def reverseGeo(request):
    url = 'https://nominatim.openstreetmap.org/reverse?'
    lat = request.GET.get('lat')
    lon = request.GET.get('lng')

    geoHeader = {'User-Agent': 'NOCTURNO'}

    geoResponse = requests.get(url, headers=geoHeader, params={
        "lat": lat, "lon": lon, "zoom": 18, "format": "json"},).json()

    return JsonResponse(geoResponse, safe=False)


# [${[_southWest["lat"], _northEast["lat"]]}]/[${[
#     _northEast["lng"],
#     _southWest["lng"],
# ]}]`s

# Zwraca party elements w map
def generateParties(request, coords):
    coords = coords.split(",")
    coords_nums = [float(el) for el in coords]
    latitude = coords_nums[:2]
    longitude = coords_nums[2:]
    near_parties = PartyModel.objects.filter(
        lat__gte=latitude[0], lat__lte=latitude[1], lng__gte=longitude[0], lng__lte=latitude[1]).order_by("date")

    participiant_parties = request.user.participant_parties.all()
    user_parties = request.user.partymodel_set.all()

    near_parties_serialized = serialize("json", near_parties)
    participiant_parties_serialized = serialize("json", participiant_parties)
    user_parties_serialized = serialize("json", user_parties)

    partiesData = [participiant_parties_serialized,
                   user_parties_serialized, near_parties_serialized]

    return JsonResponse(partiesData, safe=False)


def partyAction(request, action, party_id):
    party = PartyModel.objects.get(pk=party_id)
    user = PartyUser.objects.get(id=request.user.id)

    if action == "sign-up":
        party.participants.add(user)
    elif action == "sign-out":
        party.participants.remove(user)
    else:
        serialize_party = serialize("json", [party])
        return JsonResponse(serialize_party, safe=False)

    return JsonResponse("1", safe=False)

# Views


@login_required(login_url="login")
def mainView(request):
    user_parties = PartyModel.objects.filter(
        author=request.user).order_by("date")
    participant_parties = PartyModel.objects.filter(
        participants=request.user).exclude(author=request.user).order_by("date")
    return render(request, "main.html", {
        "user_parties": user_parties,
        "participant_parties": participant_parties
    })


class mapView(LoginRequiredMixin, View):
    template_name = "map.html"
    login_url = "login"

    def get(self, request):
        partyForm = PartyForm()
        return render(request, "map.html", {
            "partyForm": partyForm,
        })

    def post(self, request):
        partyForm = PartyForm(request.POST, request.FILES)
        attempt = 0
        if partyForm.is_valid():
            party = partyForm.save(commit=False)
            party.author = request.user
            party.save()
            party.participants.add(request.user)
            return redirect("map")
        else:
            attempt = 1

        return render(request, "map.html", {
            "partyForm": partyForm,
            "attempt": attempt
        })


class LoginUserView(LoginView):
    template_name = "login.html"
    success_url = "home"

    def get_success_url(self):
        return reverse_lazy('home')

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.add_message(self.request, messages.ERROR,
                             "WRONG! PASSWORD or USERNAME")
        return self.render_to_response(self.get_context_data(form=form))


def logoutUser(request):
    logout(request)
    return redirect("login")


class RegisterView(views.View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):

        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.age = calcAge(
                user.birth.year, user.birth.month, user.birth.day)
            user.save()

            # konfiguracja Resend
            resend.api_key = os.environ["RESEND_API_KEY"]

            # dane maila
            current_site = get_current_site(request)
            mail_subject = "Confirm your email to finish user creation"
            recipient_list = [user.email]
            mail_context = {
                "user": user,
                "domain": current_site.domain,
                "subject": mail_subject,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": emailActivationToken.make_token(user=user),
            }
            html_txt = render_to_string(
                "txt/email_confirmation.txt", mail_context)

            # renderowanie treści maila z HTML template
            html_mail = render_to_string(
                "email_confirm.html", mail_context)

           #
            msg = EmailMultiAlternatives(
                subject=mail_subject,
                body=html_txt,
                from_email="noreply@nocturno.click",
                to=recipient_list,
            )

            msg.attach_alternative(html_mail, "text/html")
            msg.send()

            return render(request, "reset_password_confirmation.html")

        return render(request, "register.html", {"form": form})


class ConfirmationView(View):
    def get(self, request, uidb64, token):
        users = get_user_model()
        user = None
        try:
            user_id = urlsafe_base64_decode(uidb64)
            user = users.objects.get(pk=user_id)
        except:

            messages.add_message(request, messages.ERROR,
                                 "Chceck your email - maybe it is wrong ❌❌")

            return redirect("email-change")

        if user is not None and emailActivationToken.check_token(user, token):
            user.is_active = True
            user.save(update_fields=["is_active"])
            return redirect("home")
        return redirect("register")


class ResetPasswordEmailView(PasswordResetView):
    template_name = "reset_password_email.html"
    email_template_name = "txt/reset_password.txt"
    subject_template_name = "txt/reset_password_subject.txt"
    html_email_template_name = "reset_password_message.html"
    success_url = "email-notification"
    from_email = "noreply@nocturno.click"


class ResetPasswordView(PasswordResetConfirmView):
    template_name = 'reset_password.html'
    success_url = '/login'
    form_class = SetPasswordForm


class EmailNotificationView(PasswordResetDoneView):
    template_name = "reset_password_confirmation.html"


# Początkowe wyświetlanie buddies -> generowanie pocztkowego html wraz z buddies uzytkownika
# BuddiesView stanowi baze dla dalszych operacji na template -> jedyny view odnoszący się do buddies który nie zwraca json response
class BuddiesView(LoginRequiredMixin, View):

    login_url = "login"

    def get(self, request):
        users_subscriptions = request.user.following.all()
        return render(request, "buddies.html", {
            "friends_relation": users_subscriptions
        })


class CheckBuddiesView(LoginRequiredMixin, View):

    login_url = "login"

    def get(self, request, party_id):
        check_query = PartyUser.objects.filter(
            participant_parties=party_id)

        new_friend_query = PartyUser.objects.all()
        user_response = list(
            request.user.following.values_list("followed__id", flat=True))

        return render(request, "check_list.html", {
            "check_query":  check_query,
            'new_friend_query': new_friend_query,
            "user_response": user_response
        })


# Zwraca 5 (10) najnowszych użytkowników dla find/yours 5/10 -> umozliwia zmiane typow i dynamiczne generowanie html bez przeładowania strony
def initFindBuddie(request):
    search_type_cookie = request.COOKIES.get("searchingType")
    user = request.user

    # Zdobywanie id zaobserwowanych przez uzytkownika
    friends_ids = list(user.following.values_list("followed__id", flat=True))

    # Sprawdzanie typu
    if search_type_cookie == "Find":
        new_friend_query = PartyUser.objects.all()

        user_response = list(new_friend_query.values(
            "id", "avatar", "username"))
        # Dla find dodatkowo zwracany friends_ids do wygenerowania odpowiedniego przycisku
        return JsonResponse([user_response, friends_ids], safe=False)

    else:
        # Kod dla Yours
        # Zwrócenie queryseta z zaobserwowanymi userami na podstawie id
        new_friend_query = PartyUser.objects.filter(
            id__in=friends_ids)

        user_response = list(new_friend_query.values(
            "id", "avatar", "username"))

        return JsonResponse([user_response], safe=False)


# Wyszukiwanie i zwracanie użytkowników
def searchingBuddie(request):
    if request.method == "GET":
        nick = request.GET.get("nick", "")
        nick_type = "username"
        search_type_cookie = request.COOKIES.get("searchingType")

        if "@" in nick:
            nick_type = "email"
        else:
            nick_type = "username"

        filter_query = f'{nick_type}__unaccent__icontains'

        user = request.user
        if search_type_cookie == "Find":
            quering_response = PartyUser.objects.filter(**{filter_query: nick})
            quering_data = list(quering_response.values(
                'avatar', "username", "id"))
            friends_ids = list(user.following.values_list(
                "followed__id", flat=True))

            return JsonResponse([quering_data, friends_ids], safe=False)
        else:

            quering_response = PartyUser.objects.filter(
                followers__follower=user, **{filter_query: nick})

            quering_data = list(quering_response.values('avatar', "username"))
            return JsonResponse(quering_data, safe=False)


def addDeleteBuddie(request):
    if request.method == "POST":
        action_friend = json.loads(request.body)

        [friendID, action] = action_friend
        user = request.user

        if str(friendID) == str(user.id):
            return JsonResponse({"error": "You can't observe yourself :("}, safe=False)

        friend = PartyUser.objects.get(id=friendID)
        if action == "add":
            user.follow(friend)
        else:
            user.un_follow(friend)

        return JsonResponse({"redirect": reverse("buddies")}, safe=False)
