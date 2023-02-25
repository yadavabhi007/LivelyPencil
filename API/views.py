from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, status
from django.views import View
from rest_framework.views import APIView
from .serializers import *
from Accounts.models import *
from django.db.models import Count
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .utils import send_otp
import os
from django.core.mail import send_mail



#Generate Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Create your views here.
class IntererstingView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        intererstings = Interesting.objects.all()
        serializer = InterestingSerializer(intererstings, many=True)
        return Response({'status':'True', 'message':'List of Intererstings', "data": serializer.data}) 


class UserRegistration(APIView):
    def post(self, request, format=None):
        if User.objects.filter(email=request.data['email']).exists():
            return Response({'status':'False', 'message':'Email Already Exists'})
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            user = user.id    
            user_id = User.objects.get(pk=user)
            book_image = request.data['stream_cover_image']
            book_name  = request.data['stream_title']
            print(user, book_image, book_name)
            data = Book.objects.create(user=user_id, book_name=book_name, book_image=book_image )
            return Response({'status':'True', 'message':'User Registration Is Succesful', 'token':token})      
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


class CheckUserView(APIView):
    def post(self, request, format=None):
        serializer = UserEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            user = User.objects.filter(email=email)
            if not user.exists():
                return Response({'status':'True', 'message':'Email Is valid.'})
            return Response({'status':'False', 'message':'Email Is Already Exists'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


class EmailVerificationView(APIView):
    def post(self, request, format=None):
        serializer = UserEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            user = User.objects.filter(email=email)
            if user.exists():
                send_otp(email)
                return Response({'status':'True', 'message':'Email Is valid. Enter OTP To Verify And Register'})
            return Response({'status':'False', 'message':'Email Is Not Exists'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


class VerifyEmailView(APIView):
    def post(self, request, format=None):
        serializer = VerifyAccountSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            otp = serializer.data['verify_email_otp']
            user = User.objects.filter(email=email)
            if not user.exists():
                return Response({'status':'False', 'message':'Invalid Email'})
            if user[0].verify_email_otp != otp:
                return Response({'status':'False', 'message':'Invalid OTP'})
            user = user.first()
            user.email_verified = True
            user.verify_email_otp = random.randint(100000, 999999)
            user.save()
            return Response({'status':'True', 'message':'Your Email Is Verified'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


class UserLoginView(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            device_token = serializer.data.get('device_token')
            user = authenticate(email=email, password=password)
            if user is not None:
                device = User.objects.filter(email=email)
                device.update(device_token=device_token)
                token = get_tokens_for_user(user)
                return Response({'status':'True', 'message':'User Login Succesfull', 'image':user.image.url, 'token':token})
            return Response({'status':'False', 'message':'Username Or Password Is Incorrect'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        # friends = User.objects.filter(id=request.user.id).aggregate(Count('friends'))
        book = Book.objects.filter(user=request.user).aggregate(Count('book_name'))
        serializer = UserProfileSerializer(instance=request.user)
        return Response({'status':'True', 'message':'View Your Profile', "book":book, "data": serializer.data})    
    def put(self, request, format=None):
        serializer = UserProfileSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'True', 'message':'User Profile Changed Succesfully'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})
    def delete(self, request, format=None):
        user = self.request.user
        user.delete()
        return Response({'status':'True', 'message':'User Account Deleted Successfully'})


class UserRoleView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = RoleSettingSerializer(instance=request.user)
        return Response({'status':'True', 'message':'View Your Role Setting', "data": serializer.data})    
    def put(self, request, format=None):
        serializer = RoleSettingSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'True', 'message':'User Role Setting Changed Succesfully'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})    


class UserNotificationSettingView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = NotificationSettingSerializer(instance=request.user)
        return Response({'status':'True', 'message':'View Your Notication Setting', "data": serializer.data})    
    def put(self, request, format=None):
        serializer = NotificationSettingSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'True', 'message':'User Notication Setting Changed Succesfully'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})    


class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
        if serializer.is_valid():
            return Response({'status':'True', 'message':'Password Changed Successfully'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordRestRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                user.save()
                send_mail(
                'Reset Your Password',
                f'Your OTP for password reset is {user.reset_password_otp}.',
                os.environ.get('EMAIL_FROM'),
                [user.email],
                fail_silently=False,
                )
                return Response({'status':'True', 'message':'OTP Sent Successfully'})
            return Response({'status':'False', 'message':'OTP Sent Unsuccessful'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordRestSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(email=serializer.data['email']).exists():
                user = User.objects.get(email=serializer.data['email'])
                if serializer.data['reset_password_otp'] == user.reset_password_otp:
                    return Response({'status':'True', 'message':'Password Reset Successfully'})
                return Response({'status':'False', 'message':'OTP did not matched'})
            return Response({'status':'False', 'message':'User does not Exist'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


class PasswordResetDoneView(APIView):
    def put(self, request):
        serializer = PasswordRestDoneSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(email=serializer.data['email']).exists():
                user = User.objects.get(email=serializer.data['email'])
                if serializer.data['reset_password_otp'] == user.reset_password_otp:
                    password = serializer.data['password']
                    user.set_password(password)
                    user.save()
                    return Response({'status':'True', 'message':'Password Reset Successfully'})
                return Response({'status':'False', 'message':'OTP did not matched'})
            return Response({'status':'False', 'message':'User does not Exist'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


class UserLogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'True', 'message':'User is Logout'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


class AddFollower(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id, format=None):
        if User.objects.filter(id=id).exclude(id=request.user.id).exists():
            user = User.objects.get(id=id)
            user.followers.add(request.user)
            request.user.followings.add(user)
            Notifications.objects.create(title='Following', message=request.user.username +' started following you').recipient.add(user)
            return Response({'status':'True', 'message':'You Started Following The User'})
        return Response({'status':'False', 'message':'You Cannot Unfollow The User'})


class AddFollowers(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        id = request.data.get('id')
        print(id)
        if User.objects.filter(id__in=id).exclude(id=request.user.id).exists():
            user = User.objects.filter(id__in=id).exclude(id=request.user.id)
            for i in user:
                i.followers.add(request.user)
                request.user.followings.add(i)
            # Notifications.objects.create(title='Following', message=request.user.username +' started following you').recipient.add(user)
            return Response({'status':'True', 'message':'You Started Following The User'})
        return Response({'status':'False', 'message':'You Cannot Follow The User'})


class RemoveFollower(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id, format=None):
        if User.objects.filter(id=id, followers=request.user).exclude(id=request.user.id).exists():
            user = User.objects.get(id=id)
            user.followers.remove(request.user)
            request.user.followings.remove(user)
            return Response({'status':'True', 'message':'You Started Unfollowing The User'})
        return Response({'status':'False', 'message':'You Cannot Unfollow The User'})


class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id, format=None):
        if User.objects.filter(id=id).exists():
            user = User.objects.get(id=id)
            usr = User.objects.filter(id=id)
            if usr.filter(followings__in=[request.user.id]):
                user.followed = True
                serializer = UserDetailSerializer(user)
                return Response({'status':'True', 'message':'View Your Profile', "data": serializer.data})
            serializer = UserDetailSerializer(user)
            return Response({'status':'True', 'message':'View Your Profile', "data": serializer.data})
        return Response({'status':'False', 'message':'User Does Not Exist'}) 


class LiveUsers(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        follow = User.objects.filter(followers__in=[request.user.id])
        unfollow = User.objects.exclude(followers__in=[request.user.id])
        for i in follow:
            i.followed = True
        user = follow.union(unfollow, all=True)
        print('follow', follow)
        print('unfollow', unfollow)
        print('user', user)
        serializer = LiveUserSerializer(user, many=True)
        return Response({'status':'True', 'message':'View Live Users', "data": serializer.data})


class FollowersList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id, format=None):
        if User.objects.filter(id=id).exists():
            user = User.objects.get(id=id)
            followers = user.followers.all()
            serializer = UserProfileSerializer(followers, many=True)
            return Response({'status':'True', 'message':'All Followers of The User', "data": serializer.data})
        return Response({'status':'False', 'message':'User Does Not Exist'}) 


class MyFollowersList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        followers = request.user.followers.all()
        serializer = UserProfileSerializer(followers, many=True)
        return Response({'status':'True', 'message':'All Followers of The User', "data": serializer.data})
  

class PopularLists(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        user = User.objects.exclude(id=request.user.id)
        serializer = UserProfileSerializer(user, many=True, context={"user":request.user.id})
        return Response({'status':'True', 'message':'View Your Profile', "data": serializer.data}) 


class PostsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response({'status':'True', 'message':'All Posts', "data": serializer.data})


class PostView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id,  format=None):
        count = Post.objects.filter(id=id)
        com = PostComment.objects.filter(post=id)
        if count.exists():
            post = Post.objects.get(id=id)
            likes = count.aggregate(Count('likes'))
            dislikes = count.aggregate(Count('dislikes'))
            comment = com.aggregate(Count('comment'))
            serializer = PostSerializer(post)
            return Response({'status':'True', 'message':'Clicked On Post', 'likes':likes, 'dislikes':dislikes, 'comment':comment, "data": serializer.data})
        return Response({'status':'False', 'message':'Post Is Unvailable'})
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'status':'True', 'message':'Post Is Saved'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})
    def put(self, request, id, format=None):
        if Post.objects.filter(id=id).exists():
            post = Post.objects.get(id=id)
            if request.user == post.user:
                serializer = PostSerializer(post, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(user=request.user)
                    return Response({'status':'True', 'message':'Post Is Saved'})
                return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})
            return Response({'status':'False', 'message':'Post Is Of Other User'})
        return Response({'status':'False', 'message':'Post Is Not Exist'})
    def delete(self, request, id, format=None):
        if Post.objects.filter(id=id, user=request.user).exists():
            post = Post.objects.get(id=id)
            post.delete()
            return Response({'status':'True', 'message':'Post Is Deleted'})
        return Response({'status':'True', 'message':'Post Is Unavailable'})


class PostLikesView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id, format=None):
        if Post.objects.filter(id=id).exists():
            # new_like, created = PostLikes.objects.get_or_create(user=request.user, post_id=id)
            get_object_or_404(Post.objects.filter(id=id)).likes.add(request.user)
            return Response({'status':'True', 'message':'Post Is Liked'})
        return Response({'status':'False', 'message':'Post Is Unavailable'})


class PostDislikesView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id, format=None):
        if Post.objects.filter(id=id).exists():
        # new_dislike, created = PostDislikes.objects.get_or_create(user=request.user, post_id=id)
            get_object_or_404(Post.objects.filter(id=id)).dislikes.add(request.user)
            return Response({'status':'True', 'message':'Post Is Disiked'})
        return Response({'status':'False', 'message':'Post Is Unavailable'})


class PostCommentView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id, format=None):
        if Post.objects.filter(id=id).exists():
            post = PostComment.objects.filter(post=id)
            serializer = PostCommentSerializer(post, many=True)
            return Response({'status':'True', 'message':'Comments Of The Posts', "data": serializer.data})
        return Response({'status':'False', 'message':'Post Not Exist'})
    def post(self, request, id, format=None):
        if Post.objects.filter(id=id).exists():
            post = Post.objects.get(id=id)
            comment = request.data.get('comment')
            new_comment = PostComment.objects.create(user=request.user, post=post, comment=comment)
            serializer = PostCommentSerializer(new_comment)
            # get_object_or_404(Post.objects.filter(id=id)).comment.add(request.user)
            return Response({'status':'True', 'message':'Comment Is Added', "data":serializer.data})
        return Response({'status':'False', 'message':'Post Is Not Available'})
    def put(self, request, id, format=None):
        if PostComment.objects.filter(id=id).exists():
            comment = PostComment.objects.get(id=id) 
            if request.user == comment.user:
                serializer = PostCommentSerializer(comment, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'status':'True', 'message':'Post Comment Updated'})
                return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})
            return Response({'status':'False', 'message':'Post Comment Is Of Other User'})
        return Response({'status':'False', 'message':'Post Comment Is Not Exist'})
    def delete(self, request, id, format=None):
        if PostComment.objects.filter(id=id, user=request.user).exists():
            comment = PostComment.objects.get(id=id) 
            comment.delete()
            return Response({'status':'True', 'message':'comment Is Deleted'})
        return Response({'status':'True', 'message':'comment Is Unavailable'})


# class SendFriendRequest(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request, id, format=None):
#         if User.objects.filter(id=id).exclude(Q(id=request.user.id) | Q(friends=request.user)).exists():
#             reciever = User.objects.get(id=id)
#             friend_request, created = FriendRequest.objects.get_or_create(sender=request.user, reciever=reciever)
#             if created:
#                 return Response({'status':'True', 'message':'Friend Request Sent'})
#             return Response({'status':'False', 'message':'Friend Request Already Sent'})
#         return Response({'status':'False', 'message':'User Is Unavailable'})


# class AcceptFriendRequest(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request, id, format=None):
#         if FriendRequest.objects.filter(id=id).exists():
#             friend_request = FriendRequest.objects.get(id=id)
#             if friend_request.reciever == request.user:
#                 friend_request.sender.friends.add(friend_request.reciever)
#                 friend_request.reciever.friends.add(friend_request.sender)
#                 friend_request.delete()
#                 return Response({'status':'True', 'message':'Friend Request Accepted'})
#             return Response({'status':'False', 'message':'Friend Request Not Accepted'})
#         return Response({'status':'False', 'message':'Friend Request Is Not Exists'})


# class DeclineFriendRequest(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request, id, format=None):
#         if FriendRequest.objects.filter(id=id).exists():
#             friend_request = FriendRequest.objects.get(id=id)
#             if friend_request.reciever == request.user:
#                 friend_request.delete()
#                 return Response({'status':'True', 'message':'Friend Request Has Declined'})
#             return Response({'status':'False', 'message':'You Can Not Decline Friend Request'})
#         return Response({'status':'False', 'message':'Friend Request Is Not Exists'})


# class UnfriendView(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request, id, format=None):
#         if User.objects.filter(id=id).exclude(username=request.user.username).exists():
#             friend = User.objects.get(id=id)
#             request.user.friends.remove(friend)
#             friend.friends.remove(request.user)
#             return Response({'status':'True', 'message':'Unfriend Successful'})
#         return Response({'status':'False', 'message':'User Is Unavailable'})


# class ViewSentRequests(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request, format=None):
#         if FriendRequest.objects.filter(sender=request.user).exists():
#             sent_requests = FriendRequest.objects.filter(sender=request.user)
#             serializer = FriendRequestSerializer(sent_requests, many=True)
#             return Response({'status':'True', 'message':'Sent Friend Requests', 'Data':serializer.data})
#         return Response({'status':'False', 'message':'No Requests'})


# class ViewRecievedRequests(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request, format=None):
#         if FriendRequest.objects.filter(reciever=request.user).exists():
#             recieved_requests = FriendRequest.objects.filter(reciever=request.user)
#             serializer = FriendRequestSerializer(recieved_requests, many=True)
#             return Response({'status':'True', 'message':'Sent Friend Requests', 'Data':serializer.data})
#         return Response({'status':'False', 'message':'No Requests'})


class SettingView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = SettingSerializer(instance=request.user)
        return Response({'status':'True', 'message':'My Settings', 'Data':serializer.data})
    def put(self, request, format=None):
        serializer = SettingSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'True', 'message':'Settings Changed Succesfully'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


class StreamView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = StreamSerializer(instance=request.user)
        return Response({'status':'True', 'message':'My Stream', 'Data':serializer.data})
    def put(self, request, format=None):
        serializer = StreamSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'True', 'message':'Stream Settings Changed Succesfully'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


# class TVSettingView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request, format=None):
#         serializer = TVSettingSerializer(instance=request.user)
#         return Response({'status':'True', 'message':'My TV Setting', "data": serializer.data})
#     def put(self, request, id, format=None):
#         serializer = TVSettingSerializer(instance=request.user, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'status':'True', 'message':'Radio Settings Changed Succesfully'})
#         return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})


# class TVChannelsView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request, format=None):
#         channels = TVChannel.objects.all()
#         serializer = TVChannelSerializer(channels, many=True)
#         return Response({'status':'True', 'message':'Popular TV Channels', "data": serializer.data})


# class TVChannelView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request, id, format=None):
#         if TVChannel.objects.filter(id=id).exists():
#             get_object_or_404(TVChannel.objects.filter(id=id)).view.add(request.user)
#             total_view = TVChannel.objects.filter(id=id).aggregate(Count('view'))
#             total_comment = TVChannelComment.objects.filter(tv_channel=id).aggregate(Count('comment'))
#             comment = TVChannel.objects.get(id=id)
#             serializer = TVChannelSerializer(comment)
#             return Response({'status':'True', 'message':'The TV Channel', 'total_view':total_view, 'total_comment':total_comment, "data": serializer.data})
#         return Response({'status':'False', 'message':'TV Channe Not Exist'})



# class TVChannelCommentView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request, id, format=None):
#         if TVChannel.objects.filter(id=id).exists():
#             comment = TVChannelComment.objects.filter(tv_channel=id)
#             serializer = TVChannelCommentSerializer(comment, many=True)
#             return Response({'status':'True', 'message':'Comments Of The Channel', "data": serializer.data})
#         return Response({'status':'False', 'message':'TV Channe Not Exist'})
#     def post(self, request, id, format=None):
#         if TVChannel.objects.filter(id=id).exists():
#             tv_channel = TVChannel.objects.get(id=id)
#             serializer = TVChannelCommentSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save(user=request.user, tv_channel=tv_channel)
#                 # get_object_or_404(TVChannel.objects.filter(id=id)).comment.add(request.user)
#                 return Response({'status':'True', 'message':'Comment Is Added', "data":serializer.data})
#             return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})
#         return Response({'status':'False', 'message':'TV Channel Comment Not Exist'})
#     def put(self, request, id, format=None):
#         if TVChannelComment.objects.filter(id=id).exists():
#             comment = TVChannelComment.objects.get(id=id) 
#             if request.user == comment.user:
#                 serializer = TVChannelCommentSerializer(comment, data=request.data, partial=True)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response({'status':'True', 'message':'TV Channel Comment Updated'})
#                 return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})
#             return Response({'status':'False', 'message':'TV Channel Comment Is Of Other User'})
#         return Response({'status':'False', 'message':'TV Channel Comment Is Not Exist'})
#     def delete(self, request, id, format=None):
#         if TVChannelComment.objects.filter(id=id, user=request.user).exists():
#             comment = TVChannelComment.objects.get(id=id) 
#             comment.delete()
#             return Response({'status':'True', 'message':'comment Is Deleted'})
#         return Response({'status':'False', 'message':'comment Is Unavailable'})


class NotificationsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        # if Notifications.objects.filter(recipient=request.user).exists():
            notification = Notifications.objects.filter(recipient=request.user).order_by('-created_at__year','-created_at__month','-created_at__day','-created_at__hour','-created_at__minute','-created_at__second')
            total = Notifications.objects.filter(recipient=request.user).exclude(is_seen=request.user).all()
            count = total.aggregate(Count('message'))
            serializer = NotificationsSerializer(notification, many=True)
            for i in total:
                i.is_seen.add(request.user)
            return Response({'status':'True', "count":count, 'message':'All Notifications', "data": serializer.data})
        # return Response({'status':'True', 'message':'Notification Is Unavailable'}, status=status.HTTP_200_OK)
    def post(self, request, format=None):
        if Notifications.objects.filter(recipient=request.user).exists():
            notification = Notifications.objects.filter(recipient=request.user)
            for i in notification:
                i.recipient.remove(request.user)
            return Response({'status':'True', 'message':'Notifications Are Cleared'})
        return Response({'status':'True', 'message':'Notification Is Unavailable'})


class NotificationsCountView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        # if Notifications.objects.filter(recipient=request.user).exists():
            total = Notifications.objects.filter(recipient=request.user).exclude(is_seen=request.user).all()
            count = total.aggregate(Count('message'))
            return Response({'status':'True', "count":count, 'message':'All Notifications'})
        # return Response({'status':'False', 'message':'Notification Is Unavailable'})


class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id, format=None):
        if Notifications.objects.filter(id=id, recipient=request.user).exists():
            notification = Notifications.objects.get(id=id)
            serializer = NotificationsSerializer(notification)
            return Response({'status':'True', 'message':'Clicked Notification', "data": serializer.data})
        return Response({'status':'True', 'message':'Notification Is Unvailable'})


class NotificationRemoveView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id, format=None):
        if Notifications.objects.filter(id=id, recipient=request.user).exists():
            notification = Notifications.objects.get(id=id)
            notification.recipient.remove(request.user)
            return Response({'status':'True', 'message':'Notification Is Deleted'})
        return Response({'status':'True', 'message':'Notification Is Unavailable'})

class AddNewBooksViews(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = BookSerializer(data=request.data)  
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'status':'True', 'message':'Book Add successfully!'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})
     
class MyBookListsViews(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        if Book.objects.filter(user_id = request.user.id).exists(): 
            data = Book.objects.filter(user_id = request.user.id).all()              
            serializer = MyBookListsSerializer(data, many=True, )
            return Response({'status':'True', 'message':'User Books Lists Details!', 'data':serializer.data})
        return Response({'status':'False', 'message':'Book Does Not Exists'})


class MyBookDetailViews(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id, format=None):
        if Book.objects.filter(user_id = request.user.id, id=id).exists():
            book = Book.objects.get(id=id)
            serializer = MyBookListsSerializer(book)
            return Response({'status':'True', 'message':'User Books Lists details!', 'data':serializer.data})
        return Response({'status':'False', 'message':'Book Does Not Exists'})
    def put(self, request, id, format=None):
        if Book.objects.filter(user_id = request.user.id, id=id).exists():
            book = Book.objects.filter(id=id)
            serializer = MyBookListsSerializer(book, data=request.data, partial=True)
            if book:       
                book_name = request.data['book_name']
                book_image = request.data.get('book_image')
                book_descriptions = request.data['book_descriptions']
                book_status = request.data['book_status']
                if book_image is not None:
                    book.update(book_name=book_name)
                    book.update(book_image=book_image)
                    book.update(book_descriptions=book_descriptions)
                    book.update(book_status=book_status)
                    return Response({'status':'True', 'message':'Book Edited Succesfully'})
                for data in book:
                    book.update(book_name=book_name)
                    book.update(book_image=data.book_image)
                    book.update(book_descriptions=book_descriptions)
                    book.update(book_status=book_status)
                return Response({'status':'True', 'message':'Book Edited Succesfully'})
            return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})
        return Response({'status':'False', 'message':'Book Does Not Exists'})
    def delete(self, request, id, format=None):
        if Book.objects.filter(user_id=request.user, id=id).exists():
            book = Book.objects.get(id=id) 
            book.delete()
            return Response({'status':'True', 'message':'Book Deleted Successfully'})
        return Response({'status':'True', 'message':'Book Is Unavailable'})


class BookListsViews(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id, format=None): 
        if Book.objects.filter(user_id = id, book_status='Public').exists():
            book = Book.objects.filter(user_id = id, book_status='Public')
            total_page = PostContent.objects.filter(book_id=book).count()
            print(total_page)
            serializer = MyBookListsSerializer(book, many=True)
            return Response({'status':'True', 'message':'User Books Lists details!', 'data':serializer.data})
        return Response({'status':'False', 'message':'Book Does Not Exists'})


class BookDetailViews(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id, format=None):
        if Book.objects.filter(id=id, book_status='Public').exclude(user_id=request.user.id).exists():
            book = Book.objects.get(id=id)
            serializer = MyBookListsSerializer(book)
            return Response({'status':'True', 'message':'User Books Lists details!', 'data':serializer.data})
        return Response({'status':'True', 'message':'Book Does Not Exists'})


class HelpView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        data = Help.objects.all()
        serializer = HelpSerializer(data, many=True)
        return Response({'status':'True', 'message':'Help Topics', 'data':serializer.data})


class HelpDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id, format=None):
        if Help.objects.filter(id=id).exists():
            data = Help.objects.get(id=id)
            serializer = HelpSerializer(data)
            return Response({'status':'True', 'message':'Help Topics', 'data':serializer.data})

            
class ProfileReport(APIView):
    def post(self, request, format=None):
        serializer = ProfileReportSerializer(data=request.data)  
        if serializer.is_valid():
            serializer.save(report_by=request.user)
            return Response({'status':'True', 'message':'Profile Reported successfully!'})
        return Response({'status':'False', 'message':'404 Bad Request', 'errors':serializer.errors})