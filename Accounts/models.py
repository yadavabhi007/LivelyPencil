from math import fabs
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.safestring import mark_safe
import random


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, stream_title, password=None):
        if not email:
            raise ValueError('User must have email')
        if not first_name:
            raise ValueError("User must have a first name")
               
        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            stream_title =stream_title,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, first_name, last_name, stream_title, password=None):
        """
        Creates and saves a superuser with the given username, email, first_name, password.
        """
        user = self.create_user(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            stream_title = stream_title,
            password = password,
        )
        user.is_admin = True
        user.save(using = self._db)
        return user    


class BaseModel(models.Model):
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  class Meta:
    abstract = True


class Interesting(BaseModel):
  category = models.CharField(max_length=100)

  def __str__(self):
    return self.category

  class Meta:
    verbose_name = ('Interesting')
    verbose_name_plural = ('Interestings')


class User(AbstractBaseUser):
  ROLE_CHOICES = [
    ("0", 'Public'),
    ("1", 'Private'),
  ]
  CHOICES = [
    ("0", 'Open'),
    ("1", 'Close'),
  ]
  username = models.CharField(max_length=100, unique=True)
  email = models.EmailField(max_length=255, unique=True)
  first_name = models.CharField(max_length = 200)
  last_name = models.CharField(max_length = 200)
  stream_title = models.CharField(max_length=100)
  stream_cover_image = models.ImageField(max_length=100, upload_to='streamcoverimage', default= "streamcoverimage/stream_cover.jpg")
  image = models.ImageField(max_length=100, upload_to='image', default= "image/image.jpg")
  role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='Public')
  device_token = models.CharField(max_length=500, null=True, blank=True)
  interesting = models.ManyToManyField(Interesting, blank=True, related_name='interesting+')
  followers = models.ManyToManyField('User', blank=True, related_name='followers+')
  followings = models.ManyToManyField('User', blank=True, related_name='followings+')
  likes = models.ManyToManyField('User', blank=True, related_name='likes+')
  # friends = models.ManyToManyField('User', blank=True, related_name='friends+')
  verify_email_otp = models.PositiveIntegerField(null=True, blank=True)
  email_verified = models.BooleanField(default=False)
  is_active = models.BooleanField(default = True)
  is_admin = models.BooleanField(default = False)
  created_at = models.DateTimeField(auto_now_add = True)
  updated_at = models.DateTimeField(auto_now = True)
  """"""
  birth_date = models.DateField(null=True, blank=True)
  country = models.CharField(max_length=100, null=True, blank=True)
  notification = models.CharField(max_length=100, choices=CHOICES, default='Open')

  """"""
  reset_password_otp = models.CharField(max_length=6, null=True, blank=True)
  # Method to Put a Random OTP in the CustomerUser table.
  def save(self, *args, **kwargs):
      number_list = [x for x in range(10)]  # Use of list comprehension
      code_items_for_otp = []
      for i in range(6):
          num = random.choice(number_list)
          code_items_for_otp.append(num)
      code_string = "".join(str(item)
                                      for item in code_items_for_otp)  # list comprehension again
      # A six digit random number from the list will be saved in top field
      self.reset_password_otp = code_string
      super().save(*args, **kwargs)

  # topic = models.CharField(max_length=100, null= True, blank=True)
  # age_group = models.CharField(max_length=100, null= True, blank=True)
  # other_tags = models.CharField(max_length=100, null= True, blank=True)
  # TV_logo = models.ImageField(upload_to='tv_logo', null= True, blank=True)
  # TV_cover = models.ImageField(upload_to='tv_cover', null= True, blank=True)
  # radio_logo = models.ImageField(upload_to='radio_logo', null= True, blank=True)
  # radio_cover = models.ImageField(upload_to='radio_cover', null= True, blank=True)

  objects = CustomUserManager()
  
  EMAIL_FIELD = "email"
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['first_name', 'last_name', 'stream_title']

  def __str__(self):
    return self.email

  def profile_image(self):
    if self.image:
      return mark_safe('<img src="{}" width="80" height="80" class="img-circle elevation-2" alt="no image"/>'.format(self.image.url))
    return None
  profile_image.short_description = 'Image'
  profile_image.allow_tags = True

  def has_perm(self, perm, obj=None):
    "Does the user have a specific permission?"
    # Simplest possible answer: Yes, always
    return self.is_admin

  def has_module_perms(self, app_label):
    "Does the user have permissions to view the app `app_label`?"
    # Simplest possible answer: Yes, always
    return True

  @property
  def is_staff(self):
    "Is the user a member of staff?"
    # Simplest possible answer: All admins are staff
    return self.is_admin
  class Meta:
      verbose_name = ('User')
      verbose_name_plural = ('Users')

def set_username(sender, instance, **kwargs):
    if not instance.username:
        username = "livelypencilfeatures"
        counter = 1
        while User.objects.filter(username=username):
            username = "livelypencilfeatures" + str(counter)
            counter += 1
        instance.username = username
models.signals.pre_save.connect(set_username, sender=User)


class Book(BaseModel):
  CHOICES = [ 
    ("0", 'Public'),
    ("1", 'Private'),
  ]
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='book')
  book_image = models.FileField(null=True, blank=True)
  book_name = models.CharField(max_length=200, null=True, blank=True)
  book_descriptions = models.TextField(null=True, blank=True)
  book_status = models.CharField(max_length=200, choices=CHOICES, default='Private')
  book_interests = models.ManyToManyField(Interesting, blank=True, related_name='Book+')
  created_at = models.DateField(auto_now_add=True, blank=True,  null=True)
  total_page = models.CharField(max_length=200, null=True, blank=True, default="0")


class PostContent(BaseModel):
  book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='post_content')
  text = models.TextField(max_length=300, null=True, blank=True )
  
  class Meta:
    verbose_name = ('Post Content')
    verbose_name_plural = ('Post Contents')


class Copytext(BaseModel):
  book_id = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copy_post_content')
  text = models.TextField(max_length=300, null=True, blank=True)


class ImageUpload(BaseModel):
  image = models.FileField(upload_to = 'images', null=True, blank=True)
  post = models.ForeignKey(PostContent, on_delete=models.CASCADE, related_name="image_id")

  def image_file(self):
    if self.image:
      return mark_safe('<img src="{}" width="80" height="80"/>'.format(self.image.url))
    return None
  image_file.short_description = 'Stream Cover Image'
  image_file.allow_tags = True

  class Meta:
    verbose_name = ('Image Upload')
    verbose_name_plural = ('Image Uploads')


class VideoUpload(BaseModel):
  video = models.FileField(upload_to = 'videos', null=True, blank=True)
  post = models.ForeignKey(PostContent, on_delete=models.CASCADE, related_name="video_id")

  class Meta:
    verbose_name = ('Video Upload')
    verbose_name_plural = ('Video Uploads')

    
class MusicUpload(BaseModel):
  music = models.FileField(upload_to = 'audio', null=True, blank=True)
  post = models.ForeignKey(PostContent, on_delete=models.CASCADE,related_name="music")

  class Meta:
    verbose_name = ('Music Upload')
    verbose_name_plural = ('Music Uploads')


class Post(BaseModel):
  ROLE_CHOICES = [
    ("Public", 'Public'),
    ("Private", 'Private'),
  ]
  TYPE_CHOICES = [
    ("Photo", 'Photo'),
    ("Video", 'Video'),
  ]
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_user')
  interersting = models.ForeignKey(Interesting, on_delete=models.CASCADE, related_name='post_interersting')
  title = models.CharField(max_length=100)
  description = models.TextField(max_length=300, null=True, blank=True)
  file = models.FileField(upload_to='post_files', null=True, blank=True)
  role = models.CharField(max_length=100, choices=ROLE_CHOICES)
  type = models.CharField(max_length=100, choices=TYPE_CHOICES)
  likes = models.ManyToManyField(User, blank=True, related_name='post_likes')
  dislikes = models.ManyToManyField(User, blank=True, related_name='post_dislikes')


  def __str__(self):
    return self.title

  class Meta:
    verbose_name = ('Post')
    verbose_name_plural = ('Posts')


# class PostLikes(BaseModel):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)

#     class Meta:
#       verbose_name = ('Post Like')
#       verbose_name_plural = ('Post Likes')


# class PostDislikes(BaseModel):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)

#     class Meta:
#       verbose_name = ('Post Dislike')
#       verbose_name_plural = ('Post Dislikes')


class PostComment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField(max_length=400)

    class Meta:
      verbose_name = ('Post Comment')
      verbose_name_plural = ('Post Comments')


# class FriendRequest(BaseModel):
#   sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
#   reciever = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reciever')


#   def __str__(self):
#     return self.sender.first_name

#   class Meta:
#     verbose_name = ('Friend Request')
#     verbose_name_plural = ('Friend Requests')


# class TVChannel(BaseModel):
#   user = models.ForeignKey(User, on_delete=models.CASCADE, null= True, blank=True, related_name='tv_channel_user')
#   stream_name = models.ForeignKey(Interesting, on_delete=models.CASCADE, related_name='tv_channel_stream')
#   topic = models.CharField(max_length=100)
#   TV_logo = models.ImageField(upload_to='tv_logo')
#   video = models.FileField(upload_to='tv_video', null= True, blank=True)
#   view = models.ManyToManyField(User, blank=True, related_name='tv_channel_view')


#   def __str__(self):
#     return self.topic

  # def tv_logo_file(self):
  #   if self.TV_logo:
  #     return mark_safe('<img src="{}" width="80" height="80" class="img-circle elevation-2"/>'.format(self.TV_logo.url))
  #   return None
  # tv_logo_file.short_description = 'TV logo'
  # tv_logo_file.allow_tags = True

#   class Meta:
#     verbose_name = ('TV Channel')
#     verbose_name_plural = ('TV Channels')


# class TVChannelComment(BaseModel):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null= True, blank=True)
#     tv_channel = models.ForeignKey(TVChannel, on_delete=models.CASCADE, null= True, blank=True)
#     comment = models.TextField(max_length=400)

#     class Meta:
#       verbose_name = ('TV Channel Comment')
#       verbose_name_plural = ('TV Channel Comments')


class Notifications(BaseModel):
  sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sender_notification')
  recipient = models.ManyToManyField(User, related_name='recipient_notification')
  title = models.CharField(max_length=100)
  message = models.TextField(max_length=1000)
  is_seen = models.ManyToManyField(User, blank=True, related_name='is_seen_notification')
  recieved_date = models.DateTimeField(auto_now_add=True)

  class Meta:
    verbose_name = ('Notification')
    verbose_name_plural = ('Notifications')


class Support(BaseModel):
  name = models.CharField(max_length=100)
  email = models.EmailField(max_length=100)
  about = models.TextField(max_length=1000)
  image = models.ImageField(upload_to='support_image')

  def image_file(self):
    if self.image:
      return mark_safe('<img src="{}" width="80" height="80"/>'.format(self.image.url))
    return None
  image_file.short_description = 'Stream Cover Image'
  image_file.allow_tags = True


class Help(BaseModel):
  heading = models.CharField(max_length=100)
  description = models.TextField(max_length=1000)


class PrivacyPolicy(BaseModel):
  heading = models.CharField(max_length=100, null=True, blank=True)
  description = models.TextField(max_length=1000)

  class Meta:
    verbose_name = ('Privacy Policy')
    verbose_name_plural = ('Privacy Policies')


class TermsAndConditions(BaseModel):
  heading = models.CharField(max_length=100, null=True, blank=True)
  description = models.TextField(max_length=1000)

  class Meta:
    verbose_name = ('Terms And Conditions')
    verbose_name_plural = ('Terms And Conditions')


class ProfileReport(BaseModel):
  report_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='report_by')
  report_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='report_to')

  class Meta:
    verbose_name = ('Profile Report')
    verbose_name_plural = ('Profile Reports')

    