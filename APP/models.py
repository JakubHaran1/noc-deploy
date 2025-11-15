import os
from io import BytesIO
from datetime import date

from django import forms
from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser

from PIL import Image
from storages.backends.s3boto3 import S3Boto3Storage


def date_checker(value):
    if date.today() > value:
        raise ValidationError(f"This date isn't correct")


class PartyUser(AbstractUser):
    username = models.CharField(
        _("Name"), max_length=30, help_text="You can pass only 30 letters username.", unique=True
    )
    email = models.EmailField(
        _("email field"), max_length=254, blank=False, unique=True
    )
    birth = models.DateField(_("birth date"))
    avatar = models.FileField(_("File"), upload_to="users_image/", blank=True)

    class Meta:
        verbose_name = "partyUser"
        verbose_name_plural = "partyUsers"

    def __str__(self):
        return f'{self.username},{self.email},{self.id}'

    def return_age(self):
        return date.today().year - self.birth.year

    def follow(self, other_user):
        if self != other_user:
            FollowModel.objects.get_or_create(
                follower=self, followed=other_user)

    def un_follow(self, other_user):
        FollowModel.objects.filter(follower=self, followed=other_user).delete()

    def has_friends(self):
        return self.following.exists()

    def save(self, *args, **kwargs):
        if self.avatar:
            try:
                storage = S3Boto3Storage()
                size = (200, 200)
                self.avatar.seek(0)

                with Image.open(self.avatar) as im:
                    im.thumbnail(size)

                    buffer = BytesIO()
                    im.save(buffer, "webp")
                    buffer.seek(0)

                    base = slugify(self.username)
                    new_name = f"{base}_thumb.webp"

                    self.avatar.save(new_name, ContentFile(
                        buffer.read()), save=False)
                    storage_name = "users_image/" + new_name
                    buffer.seek(0)
                    storage.save(storage_name, ContentFile(buffer.read()))

            except Exception as e:
                print("img error:", e)

        super().save(*args, **kwargs)


class PartyModel(models.Model):
    author = models.ForeignKey(PartyUser, on_delete=models.CASCADE)
    party_title = models.CharField(_("Party title"), max_length=100)
    description = models.CharField(
        _("Description"), blank=False, default="brak", max_length=200)
    date = models.DateField(_("Date"), validators=[date_checker])
    creation_day = models.DateField(auto_now_add=True)
    people_number = models.IntegerField(
        _("People"), validators=[validators.MinValueValidator(1)])
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
        storage = S3Boto3Storage()

        if self.file:
            try:
                self.file.seek(0)
                base = slugify(os.path.splitext(
                    os.path.basename(self.file.name))[0])
                thumb_name = f"{base}_thumbnail.webp"

                with Image.open(self.file) as im:
                    im.thumbnail((220, 110))
                    buffer = BytesIO()
                    im.save(buffer, "webp")
                    buffer.seek(0)
                    self.file_thumb.save(
                        thumb_name, ContentFile(buffer.read()), save=False)

                buffer.seek(0)
                storage_name = "party_images/" + thumb_name
                storage.save(storage_name, ContentFile(buffer.read()))

            except Exception as e:
                print("thumbnail error:", e)

        super().save(*args, **kwargs)


class PartyGroup(models.Model):
    name = models.CharField(_("Group name"), max_length=50, unique=True)
    desc = models.CharField(_("Group desc"), max_length=50)

    class Meta:
        verbose_name = "partyGroup"
        verbose_name_plural = "partyGroups"


class FollowModel(models.Model):
    follower = models.ForeignKey(
        PartyUser, on_delete=models.CASCADE, related_name="following")
    followed = models.ForeignKey(
        PartyUser, on_delete=models.CASCADE, related_name="followers")
    data_followed = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ["follower", "followed"]

    def __str__(self):
        return f'{self.follower}  -> following -> {self.followed}'
