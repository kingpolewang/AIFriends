import asyncio
import json
import os
import uuid

import websockets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class ASRView(APIView):
    """
        Vue MicVAD
             ↓
        音频上传
             ↓
        Django
             ↓
        阿里云 Realtime ASR
             ↓
        文字
    """
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        # 从请求中获取上传的音频文件，'audio'是前端表单中的文件字段名
        audio = request.FILES.get('audio')
        if not audio:
            return Response({
                'result': '音频不存在',
            })
        # 读取音频文件的二进制数据（PCM格式）
        pcm_data=audio.read()
        # 异步调用语音识别任务，将PCM音频数据转换为文字
        # asyncio.run()用于运行异步函数run_asr_task
        text=asyncio.run(self.run_asr_task(pcm_data))
        return Response({
            'result': 'success',
            'text': text
        })
    async def asr_sender(self,pcm_data,ws,task_id):
        """
            异步发送音频数据到ASR（自动语音识别）服务
            pcm_data: 二进制音频数据
            ws: WebSocket连接对象
            task_id: 任务唯一标识
        """
        chunk = 3200        # 每次发送的数据块大小（字节）
        # 将音频数据分块发送，模拟实时音频流
        for i in range(0,len(pcm_data),chunk):
            await ws.send(pcm_data[i:i+chunk])
            await asyncio.sleep(0.1)    # 暂停0.1秒，避免发送过快导致服务端压力过大

        # 音频数据发送完毕，发送结束标识
        await ws.send(json.dumps({
            "header":{
                "action": "finish-task",    # 通知服务端任务完成
                "task_id": task_id,
                "streaming": "duplex"       # 双工通信模式，表示双向通信
            },
            "payload": {
                "input": {}                 # 空的输入数据，仅作为结束标记
            }
        }))
    async def asr_receiver(self,ws):
        """
           接收ASR（自动语音识别）服务的识别结果
           ws: WebSocket连接对象
           返回: 完整的识别文本
        """
        text = ''
        async for msg in ws:
            data = json.loads(msg)      # 解析JSON消息
            event = data['header']['event'] # 获取事件类型
            if event == 'result-generated':
                output = data['payload']['output']   # 接收到识别结果
                # 检查是否有转录文本，且是否是句子结束的完整结果
                if output.get('transcription',None) and output['transcription']['sentence_end']:
                    text += output['transcription']['text']
            elif event in ['task-finished','task-failed']:
                break
        return text

    async def run_asr_task(self, pcm_data):
        task_id = uuid.uuid4().hex
        api_key = os.getenv('ALI_KEY')
        wss_url = os.getenv('WSS_URL')
        headers = {
            "Authorization": f"bearer {api_key}"
        }
        async with websockets.connect(wss_url,additional_headers=headers) as ws:
            await ws.send(json.dumps({
                "header": {
                    "action": "run-task",       #当前指令中，固定为"run-task"。
                    "task_id": task_id,
                    "streaming": "duplex"       #双工通信模式，表示双向通信
                },
                "payload": {
                    "task_group": "audio",
                    "task": "asr",
                    "function": "recognition",
                    "model": "gummy-realtime-v1",
                    "parameters": {
                        "text_type": "PlainText",
                        # "voice": "longantai_v3",  # 音色  longhouge_v3   longdaiyu_v3
                        "format": "pcm", # 音频格式
                        "sample_rate": 16000, # 采样率
                        "transcription_enabled": True , # 启用语音转录功能
                        # "volume": 50, # 音量
                        # "rate": 1, # 语速
                        # "pitch": 1 # 音调
                    },
                    "input": { # input不能省去，不然会报错
                    }
                }
            }))
            # 等待服务端返回"任务已开始"的确认消息
            async for msg in ws:
                # 解析消息，检查事件类型是否为task-started
                if json.loads(msg)['header']['event'] == 'task-started':
                    break
            # 并发执行两个任务：
            # 1. asr_sender: 发送音频数据到服务端
            # 2. asr_receiver: 接收服务端返回的识别结果
            # asyncio.gather会同时运行它们，等待两者都完成
            _,text = await asyncio.gather(
                    self.asr_sender(pcm_data,ws,task_id),
                    self.asr_receiver(ws)
                )
            return text
