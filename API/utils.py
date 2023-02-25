from django.core.mail import send_mail
from django.conf import settings
import random
from Accounts.models import User


def send_otp(email):
  subject = 'Your account verification email'
  otp = random.randint(100000, 999999)
  message = f'Your OTP is {otp}'
  email_from = settings.EMAIL_HOST_USER
  send_mail(subject, message, email_from, [email])
  user_obj = User.objects.get(email=email)
  user_obj.verify_email_otp = otp
  user_obj.save()
