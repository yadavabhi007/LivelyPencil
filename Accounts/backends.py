# from django.db.models import Q
# from django.contrib.auth import get_user_model
# from django.contrib.auth.backends import ModelBackend


# class UserAuthBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         user_model = get_user_model()
#         if username is None:
#             username = kwargs.get(user_model.USERNAME_FIELD)

#         # The `username` field is allows to contain `@` characters so
#         # technically a given email address could be present in either field,
#         # possibly even for different users, so we'll query for all matching
#         # records and test each one.
#         users = user_model._default_manager.filter(
#             Q(**{user_model.USERNAME_FIELD: username}) | Q(email__iexact=username) | Q(phone__iexact=username)
#         )

#         # Test whether any matched user has the provided password:
#         for user in users:
#             if user.check_password(password):
#                 return user
#         if not users:
#             # Run the default password hasher once to reduce the timing
#             # difference between an existing and a non-existing user (see
#             # https://code.djangoproject.com/ticket/20760)
#             user_model().set_password(password)