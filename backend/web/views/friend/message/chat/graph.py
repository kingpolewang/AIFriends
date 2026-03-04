import os
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph


#对接大模型
class ChatGraph:
    @staticmethod
    def create_app():
        """
               创建并返回一个编译好的LangGraph应用

               这个方法构建了一个简单的对话图结构：
               1. 初始化大语言模型（使用DeepSeek）
               2. 定义Agent的状态类型（包含消息列表）
               3. 创建模型调用节点
               4. 构建图结构：START -> agent -> END
        """

        # 初始化大语言模型客户端
        # ChatOpenAI 兼容OpenAI API格式的模型，这里使用的是DeepSeek
        llm=ChatOpenAI(
            model='deepseek-chat',
            openai_api_key=os.getenv('API_KEY'),
            openai_api_base=os.getenv('API_BASE'),
        )

        # 定义Agent的状态类型
        # TypedDict 是Python的类型提示，用于定义字典的结构
        class AgentState(TypedDict):
            """
                Agent的状态结构
                messages: 消息列表，使用Annotated和add_messages来定义如何合并消息
                add_messages是一个特殊的 reducer，它知道如何将新消息添加到现有消息列表中
            """
            messages: Annotated[Sequence[BaseMessage], add_messages]

        # 模型调用节点函数
        def model_call(state: AgentState) -> AgentState:
            """
                模型调用节点
                参数: state: 当前的Agent状态，包含消息列表
                返回:更新后的状态，包含模型生成的回复消息
            """
            # 调用大语言模型，传入当前状态中的所有消息
            res = llm.invoke(state['messages'])
            return {
                'messages': [res],
            }

        # 创建状态图
        # StateGraph 是LangGraph的核心类，用于构建状态图
        graph = StateGraph(AgentState)
        # 添加节点
        # add_node(节点名称, 节点函数)
        graph.add_node('agent',model_call)

        # 添加边连接
        # START是特殊的起始节点，指向agent节点
        graph.add_edge(START, 'agent')
        # agent节点指向END（结束节点）
        graph.add_edge('agent',END)

        # 编译图并返回
        # compile()会将定义的图结构编译成可执行的应用
        return graph.compile()


