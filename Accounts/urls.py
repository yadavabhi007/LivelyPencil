from django.urls import path
from . import views

urlpatterns = [
    path('<str:id>', views.HomePageView.as_view(), name='homepage'),
    path('reader/<str:id>', views.ReaderView.as_view(), name='reder'),
    path('update/<int:id>', views.UpdateView.as_view(), name='update'),
    path('upload/<int:id>',views.ImageUploadView.as_view(), name="imageupload"),
    path('video-upload/<int:id>',views.VideoUploadView.as_view(), name="videoData"),
    path('music-upload/<int:id>',views.MusicUploadView.as_view(), name="musicData"),
    path('/<int:id>', views.DeleteContentPageViews.as_view(), name="deletePage"),
    path('support/', views.SupportView.as_view(), name="support"),
    path('privacy-policy/', views.PrivacyPolicyViewView.as_view(), name="privacy-policy"),
    path('terms-and-conditions/', views.TermsAndConditionsView.as_view(), name="terms-and-conditions"),
    path('delete-image', views.DeleteImage.as_view(),  name="deleteimage"),
]