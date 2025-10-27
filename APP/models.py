import datetime
from datetime import date
from django import forms
from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError


from django.utils.translation import gettext as _
from django.utils.text import slugify

from django.contrib.auth.models import AbstractUser


import os
from io import BytesIO

from PIL import Image


def uploadAvatar(username, file):
    name = slugify(username)
    return os.path.join("users_image", name, file)


def date_checker(value):
    if date.today() > value:
        raise ValidationError(f"This date isn't correct")


class PartyUser(AbstractUser):
    username = models.CharField(
        _("Name"), max_length=30, help_text="You can pass only 30 letters username.", unique=True)
    email = models.EmailField(
        _("email field"), max_length=254, blank=False, unique=True)
    birth = models.DateField(
        _("birth date"))

    avatar = models.FileField(
        _("File"), upload_to=f"users_image/", blank=True)

    class Meta:
        verbose_name = "partyUser"
        verbose_name_plural = "partyUsers"

    def __str__(self):
        return f'{self.username},{self.email},{self.id}'

    def return_age(self):
        return (date.today().year - self.birth.year)

    def follow(self, other_user):
        if self != other_user:
            FollowModel.objects.get_or_create(
                follower=self, followed=other_user)

    def un_follow(self, other_user):

        FollowModel.objects.filter(follower=self, followed=other_user).delete()

    def has_friends(self):
        return self.following.exists()

    def save(self, *args, **kwargs):
        try:
            size = (200, 200)

            if not self.avatar.name.lower().endswith((".jpg", ".png", ".webp")):
                raise ValidationError("Wrong img type!")

            file_path = os.path.split(self.avatar.path)

            file_new_path = f'{self.username}/{file_path[1].split(".")[0]} + "_thumb.webp"'

            with Image.open(self.avatar) as im:
                im.thumbnail(size)
                bufor = BytesIO()
                im.save(bufor, "webp")
                self.avatar.save(file_new_path, bufor, save=False)
        except:
            ValueError("Wrong img")

        super().save(*args, **kwargs)


class PartyModel(models.Model):
    author = models.ForeignKey(
        PartyUser,  on_delete=models.CASCADE)
    party_title = models.CharField(_("Party title"), max_length=100)
    description = models.CharField(
        _("Description"), blank=False, default="brak", max_length=200)
    date = models.DateField(_("Date"), validators=[date_checker])
    creation_day = models.DateField(auto_now_add=True)
    people_number = models.IntegerField(_("People"),
                                        validators=[validators.MinValueValidator(1)])
    age = models.IntegerField(_("Age"), validators=[validators.MinValueValidator(
        16, "You can't invite such young person..")])
    alco = models.BooleanField(_("Alcohol"), default=False)
    file = models.FileField(_("File"), upload_to="party_images/")
    file_thumb = models.FileField(
        _("File_thumb"), upload_to="party_images/", blank=True)

    participants = models.ManyToManyField(
        PartyUser, related_name="participant_parties")
    city = models.CharField(_("city"), max_length=50)
    road = models.CharField(_("road"), max_length=100)
    house_number = models.CharField(_("house number"), max_length=20)
    lat = models.CharField(max_length=9, null=True)
    lng = models.CharField(max_length=9, null=True)

    class Meta:
        verbose_name = _("party")
        verbose_name_plural = _("parties")

    def __str__(self):
        return f"{self.party_title}: {self.date}"

    def save(self, *args, **kwargs):
        file_path = os.path.split(self.file.path)
        thumb_path = f'{self.party_title}/{file_path[1].split(".")[0]}_thumbnail.webp'
        size = (220, 110)
        try:
            # Create thumbnail
            with Image.open(self.file) as im:
                im.thumbnail(size)
                bufor = BytesIO()
                im.save(bufor, 'webp')

                # Save new wersion partie's banner in the base
                self.file_thumb.save(
                    thumb_path,
                    bufor,
                    save=False,
                )
            super().save(*args, **kwargs)

        except OSError:
            print("can not create thumbnail for", thumb_path)


class PartyGroup(models.Model):
    name = models.CharField(_("Group name"), max_length=50, unique=True)
    desc = models.CharField(_("Group desc"), max_length=50)

    class Meta:
        verbose_name = "partyGroup"
        verbose_name_plural = "partyGroups"


class FollowModel(models.Model):
    follower = models.ForeignKey(
        PartyUser,  on_delete=models.CASCADE, related_name="following")

    followed = models.ForeignKey(
        PartyUser, on_delete=models.CASCADE, related_name="followers")

    data_followed = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ["follower", "followed"]

    def __str__(self):
        return f'{self.follower}  -> following -> {self.followed}'
