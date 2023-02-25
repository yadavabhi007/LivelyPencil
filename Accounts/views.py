from ast import Not
from email.mime import image
from queue import Empty
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from .forms import ImageUploadForm, SupportForms
from django.contrib import messages
from .models import *
import json, requests


class HomePageView(View):
    def get(self, request, id):
        book = Book.objects.get(id=id)
        content = PostContent.objects.filter(book_id=book)
        total_page = PostContent.objects.filter(book_id=book).count()
        last_page = PostContent.objects.filter(book_id=id).last()
        image_data = ImageUpload.objects.all()
        form_data = ImageUploadForm()
        return render(request, 'index.html',context= {'content':content,'form_data':form_data,'image_data':image_data, 'book_id':id, 'book_data':book, 'total_page':total_page, 'last_page':last_page})   
    def post(self, request, id):
        write_content = PostContent() 
        text = request.POST.get('text')
        book = Book.objects.get(id=id)
        write_content.text = text
        write_content.book = book
        write_content.save()
        return render(request, 'index.html')


class UpdateView(View):
    def post(self ,request,id):
        write_content = PostContent.objects.filter(pk=id).first()
        text = request.POST.get('content')
        print(text)
        write_content.text = text
        write_content.save()
        return render(request, 'index.html')
     

class ReaderView(View):
    def get(self, request, id):
        book = Book.objects.get(id=id)
        content = PostContent.objects.filter(book_id=book)
        total_page = PostContent.objects.filter(book_id=book).count()
        print(total_page)
        image_data = ImageUpload.objects.all()
        form_data = ImageUploadForm()
        return render(request, 'reder.html',context= {'content':content,'form_data':form_data,'image_data':image_data, 'book_id':id, 'book_data':book, 'total_page':total_page,})


class VideoUploadView(View):
    def post(self, request,id):
        video = VideoUpload()
        page_id = PostContent.objects.filter(pk=id).first()
        upload_file = request.FILES['file_name']
        post_id = request.POST['uinque_id']
        video.video = upload_file  
        video.post = page_id
        video_data = VideoUpload.objects.create(video = upload_file, post = page_id)
        data = { 'url': video_data.video.url}
        return  JsonResponse(data)

        
class DeleteImage(View):
    def get(self, request,id):
        data = ImageUpload.objects.get(id=id)
        data.delete()


# class DeletePageContentView(View):
#     def get(self ,request,id):
#         write_content = PostContent.objects.filter(pk=id).first()-
#         text = request.POST.get('content')
#         write_content.text = text
#         write_content.save()
#         return redirect('/') 


class ImageUploadView(View):
    def post(self, request,id):
        photo = ImageUpload()
        photos_list = PostContent.objects.filter(pk=id).first()
        print("pholist list", photos_list )
        upload_file = request.FILES['file_name']
        post_id = request.POST['uinque_id']
        print("post id ", post_id)
        image_url = "<img src='"+str(upload_file)+"' width=100 height=100/>"
        print("image url new",image_url )
        photo.image = upload_file  
        photo.post = photos_list
        photo = ImageUpload.objects.create(image = upload_file, post = photos_list)
        print("photo", photo)
        data = PostContent.objects.get(id=post_id)
        print("data", data)
        url = photo.image.url 
        data.text=data.text+"<img src='http://192.168.1.30:8010"+str(url)+"' width=100 height=100/>"
        data.save()
        data = { 'url': photo.image.url}
        return  JsonResponse(data)


class MusicUploadView(View):
    def post(self, request,id):
        musics = MusicUpload()
        page_id = PostContent.objects.filter(pk=id).first()
        upload_file = request.FILES['file_name']
        post_id = request.POST['uinque_id']
        musics.music = upload_file  
        musics.post = page_id
        music_data = MusicUpload.objects.create(music = upload_file, post = page_id)
        data = {'url': music_data.music.url}
        return  JsonResponse(data)

        
class DeleteContentPageViews(View):
    def get(self, request, id):
        if PostContent.objects.filter(id=id).exists():
            data = PostContent.objects.get(id=id)
            id = data.book_id
            data.delete()        
            return redirect('homepage', id)
        else:
            return redirect('homepage', id)   


class SupportView(View):
    def get(self, request):
        return render (request, 'Accounts/support.html')
    def post(self, request):
        images = request.FILES.getlist('images')
        name = request.POST.get('name')
        email = request.POST.get('email')
        about = request.POST.get('about')
        if len(images)<=5:
            print(images)
            for image in images:
                Support.objects.create(image=image, name=name, email=email, about=about)
            messages.success(request, 'Data Sumitted Successfully')
            return render(request, 'Accounts/support.html')
        messages.error(request, 'You Can Add Max 5 Images')
        return render(request, 'Accounts/support.html')


class PrivacyPolicyViewView(View):
    def get(self, request):
        privacy_policy = PrivacyPolicy.objects.all()
        return render (request, 'Accounts/privacy-policy.html', {'privacy_policy':privacy_policy})


class TermsAndConditionsView(View):
    def get(self, request):
        terms_and_conditions = TermsAndConditions.objects.all()
        return render (request, 'Accounts/terms-and-conditions.html', {'terms_and_conditions':terms_and_conditions})