#删除角色
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from web.models.character import Character


class RemoveCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            character_id = request.data['character_id']
            # author字段：ForeignKey或OneToOneField关系
            # 双下划线：表示"跨越关系查询"
            # Character（角色） → author（外键） → UserProfile（用户资料） → user（一对一） → User（Django用户）
            # pk 是 Django 模型中主键（primary key）的通用访问方式
            # Django默认会创建一个名为 'id' 的自增主键  所以 pk 实际上指向 id 字段
            Character.objects.filter(pk=character_id,author__user=request.user).delete()
        except:
            return Response({
                'result':'系统异常,删除角色失败,请稍后重试'
            })