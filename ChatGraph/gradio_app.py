import gradio as gr
from graph_agent import GraphNLPAgent
import datetime
import json
import re
import base64

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
        mermaid_html = ""
        for i, mermaid_code in enumerate(mermaid_codes):
            mermaid_html += f'''
            <div style="text-align: center; margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;">
                <div class="mermaid" id="mermaid-{i}">
                {mermaid_code}
                </div>
            </div>
            <script>
            setTimeout(function() {{
                if (typeof mermaid !== 'undefined') {{
                    mermaid.initialize({{
                        startOnLoad: false,
                        theme: 'default',
                        flowchart: {{
                            useMaxWidth: true,
                            htmlLabels: true
                        }}
                    }});
                    const div = document.getElementById('mermaid-{i}');
                    if (div && !div.hasAttribute('data-processed')) {{
                        div.setAttribute('data-processed', 'true');
                        mermaid.init(undefined, div);
                    }}
                }}
            }}, 100);
            </script>
            '''
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
.mermaid {
    text-align: center;
    margin: 20px 0;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e9ecef;
}
.mermaid svg {
    max-width: 100%;
    height: auto;
}

'''

with gr.Blocks(css=custom_css, head="""
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
<script>
// 全局Mermaid初始化
window.mermaidInitialized = false;

function initializeMermaid() {
    if (window.mermaidInitialized) return;
    
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true
            }
        });
        window.mermaidInitialized = true;
        console.log('Mermaid initialized successfully');
    } else {
        console.log('Mermaid not loaded yet, retrying...');
        setTimeout(initializeMermaid, 100);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeMermaid();
});

// 监听HTML组件更新
function renderMermaidGraphs() {
    if (typeof mermaid === 'undefined') {
        setTimeout(renderMermaidGraphs, 100);
        return;
    }
    
    const mermaidDivs = document.querySelectorAll('.mermaid:not([data-processed])');
    mermaidDivs.forEach(function(div) {
        div.setAttribute('data-processed', 'true');
        try {
            mermaid.init(undefined, div);
            console.log('Mermaid graph rendered:', div.id);
        } catch (error) {
            console.error('Error rendering mermaid graph:', error);
        }
    });
}

// 定期检查新的Mermaid元素
setInterval(renderMermaidGraphs, 500);

// 全局弹窗函数
function showAlert(message) {
    // 创建模态弹窗
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
    `;
    
    // 创建弹窗内容
    const content = document.createElement('div');
    content.style.cssText = `
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        max-width: 400px;
        text-align: center;
        position: relative;
    `;
    
    // 添加消息内容
    content.innerHTML = `
        <div style="margin-bottom: 15px; font-size: 16px;">${message}</div>
        <button onclick="this.parentElement.parentElement.remove()" style="
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        ">确定</button>
    `;
    
    // 点击背景关闭弹窗
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    // 添加ESC键关闭功能
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && document.body.contains(modal)) {
            modal.remove();
        }
    });
    
    modal.appendChild(content);
    document.body.appendChild(modal);
}
</script>
""") as demo:
    gr.Markdown("<div id='main-title'>企业知识图谱智能问答（Neo4j + LLM）</div>")
    
    with gr.Row():
        chatbot = gr.Chatbot(elem_id="chatbot-area", height=550, render_markdown=True, show_label=False)
    
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