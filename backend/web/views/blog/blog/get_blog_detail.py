from rest_framework.response import Response
from rest_framework.views import APIView

from web.models.blog import Blog

# api/blog/detail/<int:blog_id>/
class GetBlogDetailView(APIView):
    def get(self, request,blog_id):
        try:
            blog = Blog.objects.select_related('author__user').prefetch_related('tags').get(id=blog_id)
            author = blog.author
            return Response({
                'result': 'success',
                'blog':{
                    'id':blog.id,
                    'title':blog.title,
                    'content': blog.content,
                    'cover_photo': blog.cover_photo.url if blog.cover_photo else None,
                    'tags':[tag.name for tag in blog.tags.all()],
                    'author':{
                        'user_id':author.user_id,
                        'username': author.user.username,
                        'photo':author.photo.url if author.photo else None,
                    }
                }
            })
        except Blog.DoesNotExist:
            return Response({'result':'博客不存在'},status=404)
        except Exception as e:
            return Response({'result':'系统异常'},status=500)