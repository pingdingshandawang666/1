import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import json

#设置网页logo
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

#系统提示词
system_prompt ="""
                你是一个AI女朋友，，你要符合显示中真实女友的样子；
                你对用户说的话，不能太书面化，要近乎于日常日常生活中的聊天；
                你要根据用户发送的语言，选择合适的语言进行回复；
                回复信息的时候要快，并适当的用上一些emojy表情包；
                你的名字是%s,
                你的个性是%s
             """
if'V_name' not in st.session_state:
    st.session_state.V_name='小祎琳'
if'V_nature' not in st.session_state:
    st.session_state.V_nature='活泼可爱'
if 'messages' not in st.session_state:
    st.session_state.messages=[]
if 'current_session' not in st.session_state:
    st.session_state.current_session=datetime.now().strftime('%Y-%m-%d %H-%M')

#保存会话信息的函数
def save_session():
    # 保存会话信息
    if st.session_state.current_session:
        json_data = {
            "V_name": st.session_state.V_name,
            "V_nature": st.session_state.V_nature,
            "messages": st.session_state.messages,
            "current_session": st.session_state.current_session
        }
        if not os.path.exists('json文件'):
            os.mkdir('json文件')
    # 保存会话
        with open(f'json文件/{st.session_state.current_session}.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

#遍历存在的对话名称的函数
def load_json():
    json_list=[]
    if os.path.exists('json文件'):
        for file in os.listdir('json文件'):
            if file.endswith('.json'):
                file_name = file.split('.')[0]
                json_list.append(file_name)
    return json_list
#查看历史对话中的具体信息的函数
def library_json(filename):
    try:
        if os.path.exists(f'json文件/{filename}.json'):
            with open(f'json文件/{filename}.json', 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                st.session_state.V_name = json_data['V_name']
                st.session_state.V_nature = json_data['V_nature']
                st.session_state.messages = json_data['messages']
                st.session_state.current_session = json_data['current_session']
    except Exception:
        st.error('文件不存在')

#删除文件的函数
def delete_json(filename):
    try:
        if os.path.exists(f'json文件/{filename}.json'):
            os.remove(f'json文件/{filename}.json')
            if session == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = datetime.now().strftime('%Y-%m-%d %H-%M')
    except Exception:
        st.error('文件不存在')

#遍历聊天记录
for message in st.session_state.messages:
    st.chat_message(message['role']).write(message['content'])

#黄设置侧边栏
with st.sidebar:
    st.title("AI智能伴侣")
    st.subheader('对话管理')
    if st.button("新建对话", use_container_width=True, icon="✏️"):
        save_session()
    #新建对话信息
        if st.session_state.messages:
            st.session_state.messages = []
            st.session_state.current_session = datetime.now().strftime('%Y-%m-%d %H-%M')
            save_session()
            st.rerun ()
    st.text('对话历史')
    sessions_list=load_json()
    for session in sessions_list:
        #将一行标题，分割为两个
        col1, col2 = st.columns([4, 1])
        with col1:
            # 加载对话
            if st.button(session, use_container_width=True, icon='✉', key=f'load{session}',type='primary' if session==st.session_state.current_session else 'secondary'):
                library_json(session)
                st.rerun()
        with col2:
            #删除对话
            if st.button('',use_container_width=True, icon='❌', key=f'delete{session}'):
                delete_json(session)
                st.rerun()
     #分割线
    st.divider()

    st.subheader('伴侣信息')
    #设置输入框：默认选项
    V_name=st.text_input('昵称',placeholder='请输入昵称',value=st.session_state.V_name)
    if V_name:
        st.session_state.V_name=V_name
    V_nature=st.text_area('个性',placeholder='性格',value=st.session_state.V_nature)
    if V_nature:
        st.session_state.V_nature=V_nature

#输入框
prompt = st.chat_input("请说出你的问题")
if prompt:
    st.chat_message("user",avatar="🤠").write(prompt)
    # 保存用户提示词
    st.session_state.messages.append({"role": "user", "content": prompt})
    #调用大模型
    api_key = st.secrets.get("DEEPSEEK_API_KEY", os.environ.get('DEEPSEEK_API_KEY'))
    if not api_key:
        st.error("请先设置 DEEPSEEK_API_KEY")
        st.stop()
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.V_name,st.session_state.V_nature)},
            *st.session_state.messages
        ],
        stream=True
    )
    #
    # st.chat_message("assistant",avatar="👧").write(response.choices[0].message.content)
    # #保存大模型返回的答案
    # st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
    response_message=st.empty()
    #设置流式输出
    fill_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            character=chunk.choices[0].delta.content
            fill_response += character
            response_message.chat_message("assistant",avatar="👧").write(fill_response)
    st.session_state.messages.append({"role": "assistant", "content": fill_response})
    save_session()


