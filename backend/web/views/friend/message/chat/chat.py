import json
from http.client import responses

from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from web.models.friend import Friend
from web.views.friend.message.chat.graph import ChatGraph

# 定义一个伪渲染器，防止 DRF 报错
class SSERenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'txt'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class MessageChatView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (SSERenderer,)
    def post(self, request):
        friend_id = request.data.get('friend_id')
        message = request.data.get('message').strip()
        if not message:
            return Response({'result': '消息不能为空'})
        friends = Friend.objects.filter(id=friend_id,me__user=request.user)
        if not friends.exists():
            return Response({
                'result':'好友不存在'
            })
        friend = friends.first()
        app=ChatGraph.create_app()
        inputs={
            'messages':[HumanMessage(content=message)],
        }
        # 处理流式消息事件的生成器函数，主要作用是将AI模型的流式输出转换为Server-Sent Events (SSE) 格式
        # yield是Python的生层器
        def event_stream():
            final_usage = {}        # 用于存储最终的token使用统计信息
            # 从app.stream获取消息和元数据，stream_mode="messages"表示以消息块形式返回
            for msg, metadata in app.stream(inputs, stream_mode="messages"):
                # 检查消息是否为BaseMessageChunk类型（消息块）
                if isinstance(msg, BaseMessageChunk):
                    # 如果消息包含实际内容，将其包装为SSE格式
                    if msg.content:
                        # 使用json.dumps确保中文正确显示（ensure_ascii=False）
                        yield f"data: {json.dumps({'content': msg.content}, ensure_ascii=False)}\n\n"
                    # 检查并记录token使用统计信息（如输入 / 输出token数）
                    if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                        final_usage = msg.usage_metadata         #持续更新，最终保留最后一条统计
            # 发送流式结束标记
            yield "data: [DONE]\n\n"
            # 打印最终的token使用统计（仅用于调试/监控）
            print(final_usage)
        for data in event_stream():
            print(data)

        # 创建流式HTTP响应
        # StreamingHttpResponse是Django的特殊响应类，用于流式传输数据
        # event_stream()是生成器函数，会持续产生数据并推送给客户端
        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        # 设置缓存控制头，禁用缓存
        # 确保客户端不会缓存SSE数据，实现真正的实时推送
        response['Cache-Control'] = 'no-cache'
        # 返回流式响应
        # 连接将保持打开状态，持续推送数据直到event_stream()结束
        return response