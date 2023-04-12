from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User
from django.contrib.auth.password_validation import validate_password


class UserRegisterSerializer(serializers.ModelSerializer):
    #email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password], style = {"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, required=True, style={"input_type": "password",},)
    username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    full_name = serializers.CharField(required=True)
    age = serializers.IntegerField(required=True)
    #gender = serializers.CharField(required=True)
    #location = serializers.CharField(required=True)
    
    
    class Meta:
        model = User
        fields = ['user_id', 'full_name', 'username', 'age', 'phone_number',]
        
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {
                    "password": "Passwords must match."
                }
            )
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data["username"], full_name=validated_data["full_name"], age=validated_data["age"],
                                        phone_number=validated_data['phone_number'],)
        user.set_password(validated_data["password"])
        user.save()
        
        return user
    
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        if phone_number and password:
            user = authenticate(phone_number=phone_number, password=password)

            if not user:
                msg = 'Unable to authenticate with provided credentials'
                raise serializers.ValidationError(msg, code='authentication')

            if not user.is_active:
                msg = 'User account is disabled'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "phone_number" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data