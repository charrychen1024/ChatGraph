import gradio as gr
from graph_agent import GraphNLPAgent
import datetime
import json
import re
import base64
from urllib.parse import quote

# 初始化Agent
graph_agent = GraphNLPAgent()

##
# 用于存储对话历史（问题、回答、cypher）
chat_history = []

def extract_mermaid_from_response(response_text):
    """从回复中提取Mermaid代码块"""
    import re
    
    # 检测Mermaid代码块
    mermaid_pattern = r'```mermaid\s*\n(.*?)\n```'
    matches = re.findall(mermaid_pattern, response_text, re.DOTALL)
    
    if matches:
        # 移除Mermaid代码块，只保留文本部分
        for mermaid_code in matches:
            response_text = response_text.replace(f'```mermaid\n{mermaid_code}\n```', '')
        
        # 清理多余的换行和分隔符
        response_text = re.sub(r'\n\s*---\s*\n\s*\*\*关系网络图：\*\*\s*\n', '\n\n', response_text)
        response_text = response_text.strip()
        
        return response_text, matches
    else:
        return response_text, []

# 辅助函数：将 Mermaid 代码转换为 SVG 图像
# 增强版中文兼容转换函数
def mermaid_to_svg(mermaid_code):
    # 处理中文编码
    encoded = mermaid_code.encode('utf-8')
    
    # 双重安全编码方案
    base64_bytes = base64.urlsafe_b64encode(encoded)
    base64_string = base64_bytes.decode('ascii').rstrip('=')
    
    # 替代方案：URL 编码（更可靠）
    url_encoded = quote(mermaid_code, safe='')
    
    # 优先使用 base64，失败时回退到 URL 编码
    return f"https://mermaid.ink/svg/{base64_string}"

# 修改后的输出处理
def process_output(mermaid_codes):
    output_html = ""
    
    for i, code in enumerate(mermaid_codes):
        svg_url = mermaid_to_svg(code)
        output_html += f"""
        <div style="margin: 20px 0; text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;">
            <h4 style="margin-bottom: 15px; color: #333;">关系网络图 {i+1}</h4>
            <img src="{svg_url}" alt="Mermaid Diagram" 
                 style="max-width: 100%; border: 1px solid #eee; padding: 10px; border-radius: 6px; background: white;">
        </div>
        """
    
    return output_html

def chat_fn(message, history):
    """处理聊天消息，支持流式输出"""
    yield "🤔 正在思考，请稍候...", []
    stream = graph_agent.stream_query(message)
    answer = ""
    cypher = None
    for partial in stream:
        answer = partial
        if not cypher and "Cypher:" in str(partial):
            match = re.search(r'Cypher:\s*(MATCH[\s\S]+?)(?:\n\n|$)', str(partial))
            if match:
                cypher = match.group(1).strip()
        yield answer, []
    chat_history.append({
        'question': message,
        'answer': answer,
        'cypher': cypher
    })
    
    # 提取Mermaid代码和清理文本
    clean_answer, mermaid_codes = extract_mermaid_from_response(answer)
    
    # 将Mermaid图形嵌入到回复中
    if mermaid_codes:
        mermaid_html = process_output(mermaid_codes)
        clean_answer += f"\n\n**关系网络图：**\n{mermaid_html}"
    
    if cypher:
        final_answer = f"{clean_answer}\n\n---\n**Cypher:**\n```\n{cypher}\n```"
        yield final_answer, []
    else:
        yield clean_answer, []

def clear_fn():
    """清空对话历史和Agent内存"""
    global chat_history
    chat_history.clear()
    graph_agent.memory.clear()
    return []

def export_fn():
    """导出聊天历史到JSON文件"""
    import os
    
    # 确保chat_history不为空
    if not chat_history:
        return None, "❌ 没有聊天历史可导出"
    
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"chat_history_{now}.json"
    
    # 获取当前工作目录
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=2)
        print(f"聊天历史已导出到: {file_path}")
        # 返回文件路径和成功提示
        return file_path, f"✅ 聊天历史已成功导出到: {filename}"
    except Exception as e:
        print(f"导出失败: {e}")
        # 返回错误提示
        return None, f"❌ 导出失败: {str(e)}"

def show_alert_message(message):
    """显示弹窗消息"""
    return f"""
    <script>
    alert('{message}');
    </script>
    """

# 简洁的CSS样式
custom_css = '''
/* 基础样式重置 */
* {
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0;
    padding: 0;
    height: 100vh;
    overflow: hidden;
}

/* 主容器 */
.gradio-container {
    height: 100vh !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 20px !important;
    display: flex !important;
    flex-direction: column !important;
    background: #f5f5f5;
}

/* 标题 */
#main-title {
    text-align: center;
    font-size: 2rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 20px;
    padding: 10px 0;
}

/* 聊天区域 */
#chatbot-area {
    flex: 1 !important;
    height: calc(100vh - 200px) !important;
    min-height: 300px;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    background: white;
    overflow-y: auto;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 聊天消息样式 */
#chatbot-area .message {
    # margin-bottom: 12px;
    # padding: 12px 16px;
    # border-radius: 8px;
    max-width: 100%;
    word-wrap: break-word;        /* 在单词内换行 */
    word-break: break-word;       /* 适合中文的换行 */
    overflow-wrap: break-word;    /* 现代浏览器标准 */
    line-height: 0.8;
}

#chatbot-area .user-message {
    background: #007bff;
    color: white;
    margin-left: auto;
}

#chatbot-area .bot-message {
    background: #f8f9fa;
    color: #333;
    border: 1px solid #e9ecef;
}

/* 输入区域 - 固定在底部 */
#input-row {
    position: sticky;
    bottom: 0;
    background: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
    margin-top: auto;
}

/* 输入框 */
#input-box textarea {
    font-size: 14px;
    padding: 12px 16px;
    border-radius: 8px;
    border: 1px solid #ddd;
    resize: none;
    min-height: 45px;
    max-height: 120px;
    width: 100% !important;
    box-sizing: border-box;
}

#input-box textarea:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

#input-box {
    width: 100% !important;
    flex: 1;
}

/* 按钮样式 */
#send-btn, #clear-btn, #export-btn {
    padding: 8px 16px;
    border-radius: 6px;
    border: none;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

#send-btn {
    background: #007bff;
    color: white;
}

#send-btn:hover {
    background: #0056b3;
}

#clear-btn {
    background: #dc3545;
    color: white;
}

#clear-btn:hover {
    background: #c82333;
}

#export-btn {
    background: #28a745;
    color: white;
}

#export-btn:hover {
    background: #218838;
}

/* 滚动条样式 */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}

/* 代码块样式 */
pre {
    background: #f8f9fa;
    color: #333;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    border: 1px solid #e9ecef;
}

code {
    background: #f1f3f4;
    color: #333;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Monaco', 'Menlo', monospace;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .gradio-container {
        padding: 10px;
    }
    
    #main-title {
        font-size: 1.5rem;
        margin-bottom: 15px;
    }
    
    #chatbot-area {
        height: calc(100vh - 180px) !important;
        padding: 15px;
    }
    
    #input-row {
        padding: 10px;
    }
    
    #send-btn, #clear-btn, #export-btn {
        padding: 6px 12px;
        font-size: 12px;
    }
}
'''

with gr.Blocks(css=custom_css) as demo:
    # 主标题
    gr.Markdown("<div id='main-title'>企业知识图谱智能问答</div>")
    
    # 聊天区域
    with gr.Row():
        chatbot = gr.Chatbot(
            elem_id="chatbot-area", 
            height=600, 
            render_markdown=True, 
            show_label=False,
            container=True,
            bubble_full_width=True
        )
    
    # 输入和控制区域
    with gr.Row(elem_id="input-row"):
        with gr.Column(scale=15):
            msg = gr.Textbox(
                label="", 
                placeholder="请输入您的问题，例如：陈建投资了哪些公司？", 
                elem_id="input-box",
                lines=1,
                max_lines=3
            )
        with gr.Column(scale=5, min_width=200):
            with gr.Row():
                send_btn = gr.Button("发送", elem_id="send-btn", size="sm")
                clear_btn = gr.Button("清空", elem_id="clear-btn", size="sm")
                export_btn = gr.Button("导出", elem_id="export-btn", size="sm")
            download_file = gr.File(label="下载历史", visible=False, elem_id="download-file")
    
    # 帮助信息
    with gr.Accordion("💡 使用帮助", open=False):
        gr.Markdown("""
        ### 使用说明
        
        **基本功能：**
        - 输入问题，系统会自动分析并生成Cypher查询
        - 支持企业关系查询、投资关系、人员关系等
        - 自动生成关系网络图可视化
        
        **示例问题：**
        - 张伟投资了哪些公司？
        - 阿里巴巴集团有哪些子公司？
        - 陈建和李明之间有什么关系？
        - 哪些公司被腾讯投资了？
        
        **特殊功能：**
        - 关系网络图会在下方单独区域显示
        - 使用"导出"保存对话记录
        - 使用"清空"开始新的对话
        """)

    # 处理消息的函数
    def user_send(user_message, chat_history):
        chat_history = chat_history or []
        
        # 检查是否已经处理过这个消息
        if chat_history and len(chat_history) > 0 and chat_history[-1][0] == user_message:
            return "", chat_history
        
        # 立即显示用户问题和等待消息
        current_history = chat_history + [(user_message, "🤔 正在思考，请稍候...")]
        yield "", current_history
        
        # 流式处理回复
        final_response = None
        for response, mermaid_codes in chat_fn(user_message, chat_history):
            final_response = response
            # 只更新等待消息，不添加到聊天历史
            current_history = chat_history + [(user_message, response)]
            yield "", current_history
        
        # 最终结果，添加到聊天历史
        if final_response:
            chat_history.append((user_message, final_response))
            yield "", chat_history
        else:
            yield "", chat_history

    send_btn.click(user_send, [msg, chatbot], [msg, chatbot])
    msg.submit(user_send, [msg, chatbot], [msg, chatbot])
    clear_btn.click(clear_fn, outputs=[chatbot])
    
    def export_with_alert():
        file_path, status = export_fn()
        if status.startswith("✅"):
            return file_path, f"""
            <script>
            showAlert('{status}');
            </script>
            """
        elif status.startswith("❌"):
            return file_path, f"""
            <script>
            showAlert('{status}');
            </script>
            """
        else:
            return file_path, ""
    
    export_btn.click(export_with_alert, outputs=[download_file, gr.HTML(visible=False)])

if __name__ == "__main__":
    demo.launch() 