#更新博客
#/api/blog/update/
from datetime import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from web.models.blog import Blog, Tag


class UpdateBlogView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            blog_id = request.data.get('blog_id')
            title = request.data.get('title')
            content = request.data.get('content')
            tag_names=request.data.get('tags',[])
            blog=Blog.objects.get(id=blog_id,author__user=request.user)
            blog.title=title
            blog.content=content
            blog.update_time=timezone.now()
            blog.save()
            #更新标签
            blog.tags.clear()
            for name in tag_names:
                tag,_=Tag.objects.get_or_create(name=name)
                blog.tags.add(tag)
            return Response({
                'result': 'success',
            })
        except:
            return Response({
                'result':'系统异常，请稍后重试'
            })