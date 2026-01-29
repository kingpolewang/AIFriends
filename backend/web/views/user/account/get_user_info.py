from os import access

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from web.models.user import UserProfile


class GetUserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            # refresh = RefreshToken.for_user(user)
            # access = str(refresh.access_token)
            print(user.access_token)
            return Response({
                'result': 'success',
                'user_id': user.id,
                'username': user.username,
                'photo': user_profile.photo.url,
                'profile': user_profile.profile,
                # 'access': access,
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })
