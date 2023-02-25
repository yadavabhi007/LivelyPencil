from rest_framework import serializers
from Accounts.models import *
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class InterestingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interesting
        fields = '__all__'
       

class UserEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ['email']


class VerifyAccountSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ['email', 'verify_email_otp']


class UserRegistrationSerializer(serializers.ModelSerializer):
    interesting = serializers.PrimaryKeyRelatedField(
        queryset=Interesting.objects.all(),
        many=True,
        required=False)
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    stream_title = serializers.CharField()
    stream_cover_image = serializers.ImageField()
    image = serializers.ImageField()
    role = serializers.CharField()
    class Meta:
        model = User
        fields = ['email', 'device_token', 'first_name', 'last_name', 'stream_title', 'stream_cover_image', 'image', 'role', 'interesting', 'password']
        extra_kwargs = {
            'password':{'write_only':True},
        }

    def create(self, validated_data):
        user = User.objects.create(
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name  = validated_data['last_name'],
            stream_title = validated_data['stream_title'],
            stream_cover_image  = validated_data['stream_cover_image'],
            image = validated_data['image'],
            role  = validated_data['role'],
        )
        category = validated_data['interesting']
        user.interesting.set(category)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    device_token = serializers.CharField(max_length=500, required=False)
    class Meta:
        model = User
        fields = ['email', 'device_token', 'password']


class PasswordRestRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordRestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_password_otp = serializers.CharField()


class PasswordRestDoneSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_password_otp = serializers.CharField()
    password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    total_book = serializers.SerializerMethodField()
    last_stream = serializers.SerializerMethodField()
    
    def get_total_book(self, obj):
        user = self.context.get('user')
        data = Book.objects.filter(user=user).count()
        return  data

    def get_last_stream(self, obj):
        user = self.context.get('user')
        data = Book.objects.filter(user=user).last()
        return data.created_at

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'stream_title',  'stream_cover_image', 'image', 'created_at', 'updated_at', 'followers_count', 'likes_count', 'total_book', 'last_stream']


class UserDetailSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    followed = serializers.BooleanField(default=False)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'stream_title', 'stream_cover_image', 'image', 'created_at', 'updated_at', 'followers_count', 'likes_count', 'followed']


class LiveUserSerializer(serializers.ModelSerializer):
    followed = serializers.BooleanField(default=False)
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'stream_title', 'stream_cover_image', 'image', 'created_at', 'updated_at', 'followers_count', 'likes_count', 'followed']


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'stream_title', 'image', 'birth_date', 'country']


class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'stream_title', 'stream_cover_image', 'created_at']


class RoleSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['notification']


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True, style={'input_type':'password'},)
    new_password = serializers.CharField(max_length=128, write_only=True, required=True, style={'input_type':'password'},)

    def validate_old_password(self, value):
        user = self.context.get('user')
        if not user.check_password(value):
            raise serializers.ValidationError(
                ('Your old password was entered incorrectly. Please enter it again.')
            )
        return value

    def validate(self, data):
        password = data.get('new_password')
        user = self.context.get('user')
        user.set_password(password)
        user.save()
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class PagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostContent
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    # likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    # dislikes_count = serializers.IntegerField(source='dislikes.count', read_only=True)
    class Meta:
        model = Post
        fields = '__all__'


class PostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = '__all__'


# class FriendRequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FriendRequest
#         fields = '__all__'



# class RadioSettingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'interesting', 'topic', 'age_group', 'other_tags', 'radio_logo', 'radio_cover']


# class TVSettingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'interesting', 'topic', 'age_group', 'other_tags', 'TV_logo', 'TV_cover']


# class TVChannelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TVChannel
#         fields = '__all__'


# class TVChannelCommentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TVChannelComment
#         fields = '__all__'


class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['book_name', 'book_descriptions', 'book_image', 'book_status', 'book_interests']


class MyBookListsSerializer(serializers.ModelSerializer):
    total_page = serializers.SerializerMethodField()
    def get_total_page(self,obj,):
        total_page = PostContent.objects.filter(book_id=obj).count()
        return total_page  
    class Meta:
        model = Book
        fields = [ 'id','user', 'book_name','book_descriptions', "total_page", 'book_image', 'book_status', 'book_interests', 'created_at' ]


class BookListsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [ 'id', 'book_name','book_descriptions', 'book_image', 'book_interests']


class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = ['heading']


class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = '__all__'


class ProfileReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileReport
        fields = '__all__'