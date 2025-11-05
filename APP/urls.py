
from django.urls import path, include
from APP.views import reverseGeo, searchingBuddie, initFindBuddie, addDeleteBuddie, mainView, mapView, LoginUserView, RegisterView, ConfirmationView, ResetPasswordEmailView, ResetPasswordView, EmailNotificationView, BuddiesView, generateParties, partyAction, CheckBuddiesView, logoutUser

urlpatterns = [
    path("", mainView, name="home"),
    path("map", mapView.as_view(), name="map"),
    path("map/generate-parties/<coords>",
         generateParties, name="generateParties"),

    path("map/<action>/<party_id>", partyAction, name="party-action"),
    path("geocode-reverse", reverseGeo, name="reverseGeo"),

    path("login", LoginUserView.as_view(), name="login"),
    path("logout", logoutUser, name="logout"),

    path("register", RegisterView.as_view(), name="register"),
    path("email-confirmation/<uidb64>/<token>",
         ConfirmationView.as_view(), name="activate_email"),

    path('reset-password', ResetPasswordEmailView.as_view(), name='reset-password'),
    path('change-password/<uidb64>/<token>',
         ResetPasswordView.as_view(), name='change-password'),

    path('email-notification', EmailNotificationView.as_view(),
         name='email-notification'),

    path("buddies", BuddiesView.as_view(), name="buddies"),
    path("buddies/find-buddie/", searchingBuddie, name="searchBuddie"),
    path('buddies/initial-find/<party_id>',
         CheckBuddiesView.as_view(), name="check_party"),
    path('buddies/initial-find/', initFindBuddie, name="init_find"),
    path("buddies/action-buddie/", addDeleteBuddie, name="add_delete_buddie"),
]
