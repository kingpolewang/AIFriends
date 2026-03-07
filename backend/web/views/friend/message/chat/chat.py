import json
from pprint import pprint

from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk, AIMessage, SystemMessage
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from web.models.friend import Friend, Message, SystemPrompt
from web.views.friend.message.chat.graph import ChatGraph
from web.views.friend.message.memory.update import update_memory


# 定义一个伪渲染器，防止 DRF 报错
class SSERenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'txt'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

# 添加系统提示词
def add_system_prompt(state,friend):
    msgs=state['messages']
    system_prompts=SystemPrompt.objects.filter(title='回复').order_by('order_number')
    prompt=''
    for sp in system_prompts:
        prompt+=sp.prompt
    prompt += f"\n[角色性格]\n{friend.character.profile}\n"
    prompt += f"【长期记忆】\n{friend.memory}\n"
    return {
        'messages': [SystemMessage(prompt)]+msgs,
    }
# 添加最近的消息
def add_recent_message(state,friend):
    msgs=state['messages']
    message_raw=list(Message.objects.filter(friend=friend).order_by('-id')[:20])
    message_raw.reverse()
    print(f"message_raw:    {message_raw}")
    messages=[]
    for m in message_raw:
        # LangChain 库的代码，用于创建一个人类消息
        # HumanMessage 是 LangChain 中的一个消息类型，用于表示用户/人类发送的消息
        messages.append(HumanMessage(m.user_message))
        messages.append(AIMessage(m.output))
    return {
        'messages': msgs[:1]+messages+msgs[-1:],
    }
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
        inputs=add_system_prompt(inputs,friend)
        inputs=add_recent_message(inputs,friend)
        # pprint(inputs)
        # 处理流式消息事件的生成器函数，主要作用是将AI模型的流式输出转换为Server-Sent Events (SSE) 格式
        # yield是Python的生层器
        def event_stream():
            full_output = ''
            full_usage = {}        # 用于存储最终的token使用统计信息
            # 从app.stream获取消息和元数据，stream_mode="messages"表示以消息块形式返回
            for msg, metadata in app.stream(inputs, stream_mode="messages"):
                # 检查消息是否为BaseMessageChunk类型（消息块）
                if isinstance(msg, BaseMessageChunk):
                    # 如果消息包含实际内容，将其包装为SSE格式
                    if msg.content:
                        full_output += msg.content
                        # 使用json.dumps确保中文正确显示（ensure_ascii=False）
                        yield f"data: {json.dumps({'content': msg.content}, ensure_ascii=False)}\n\n"
                    # 检查并记录token使用统计信息（如输入 / 输出token数）
                    if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                        full_usage = msg.usage_metadata         #持续更新，最终保留最后一条统计
            # 发送流式结束标记
            yield "data: [DONE]\n\n"
            # 打印最终的token使用统计（仅用于调试/监控）
            print(full_usage)
            input_tokens = full_usage.get('input_tokens',0)
            output_tokens = full_usage.get('output_tokens',0)
            total_tokens = full_usage.get('total_tokens',0)
            Message.objects.create(
                friend=friend,
                user_message=message[:1000],
                input = json.dumps(
                    [m.model_dump() for m in inputs['messages'] ],
                    ensure_ascii=False,
                )[:20000],
                output=full_output[:1000],
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
            )
            # 每五次对话更新一次长期记忆
            if Message.objects.filter(friend=friend).count() % 1 ==0:
                update_memory(friend)

        # for data in event_stream():
        #     print(data)

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