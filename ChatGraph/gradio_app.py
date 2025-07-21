import gradio as gr
from graph_agent import GraphNLPAgent
import datetime
import json
import re

# 初始化Agent
graph_agent = GraphNLPAgent()

##
# 用于存储对话历史（问题、回答、cypher）
chat_history = []

def chat_fn(message, history):
    """处理聊天消息，支持流式输出"""
    yield "🤔 正在思考，请稍候..."
    stream = graph_agent.stream_query(message)
    answer = ""
    cypher = None
    for partial in stream:
        answer = partial
        if not cypher and "Cypher:" in str(partial):
            match = re.search(r'Cypher:\s*(MATCH[\s\S]+?)(?:\n\n|$)', str(partial))
            if match:
                cypher = match.group(1).strip()
        yield answer
    chat_history.append({
        'question': message,
        'answer': answer,
        'cypher': cypher
    })
    if cypher:
        final_answer = f"{answer}\n\n---\n**Cypher:**\n```\n{cypher}\n```"
        yield final_answer

def clear_fn():
    chat_history.clear()
    graph_agent.memory.clear()
    return None

def export_fn():
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"chat_history_{now}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)
    return filename

custom_css = '''
#main-title {text-align:center; font-size:2rem; font-weight:600; margin-bottom: 0.5em;}
#chatbot-area {height: 60vh; min-height: 350px;}
#input-row {margin-top: 0.5em; align-items: center !important;}
#input-row .gr-box {display: flex; align-items: center;}
#input-box textarea {
    font-size:1.1em; min-height:2.5em; height:2.5em !important; line-height:2.5em !important;
    padding-top: 0.2em !important; padding-bottom: 0.2em !important; box-sizing: border-box; resize: none;
}
#send-btn, #clear-btn, #export-btn {
    min-width: 90px; max-width: 120px; height: 2.5em; font-size:1em; margin-left: 0.5em;
    vertical-align: middle; padding: 0 !important;
}
#input-box {margin-bottom: 0 !important;}
#download-file {margin-left: 0.5em;}
'''

with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("<div id='main-title'>企业知识图谱智能问答（Neo4j + LLM）</div>")
    with gr.Row():
        chatbot = gr.Chatbot(elem_id="chatbot-area", height=550)
    with gr.Row(elem_id="input-row"):
        with gr.Column(scale=8):
            msg = gr.Textbox(label="", placeholder="请输入您的问题，例如：陈建投资了哪些公司？", elem_id="input-box")
        with gr.Column(scale=2, min_width=220):
            with gr.Row():
                send_btn = gr.Button("发送", elem_id="send-btn")
                clear_btn = gr.Button("清空对话", elem_id="clear-btn")
                export_btn = gr.Button("导出历史", elem_id="export-btn")
                download_file = gr.File(label="下载历史", visible=False, elem_id="download-file")

    def user_send(user_message, chat_history):
        chat_history = chat_history or []
        for response in chat_fn(user_message, chat_history):
            chat_history.append((user_message, response))
            yield "", chat_history

    send_btn.click(user_send, [msg, chatbot], [msg, chatbot])
    msg.submit(user_send, [msg, chatbot], [msg, chatbot])
    clear_btn.click(lambda: ([], clear_fn()), None, [chatbot])
    export_btn.click(lambda: (export_fn(), True), None, [download_file])

if __name__ == "__main__":
    demo.launch() 