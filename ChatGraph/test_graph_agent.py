from graph_agent import GraphNLPAgent
from langchain_neo4j import Neo4jGraph
import re

if __name__ == "__main__":
    agent = GraphNLPAgent()
    questions = [
        "你好，你是谁？",
        "你有什么功能？",
        "今天天气怎么样？",
        "陈建投资了哪些公司？",
        "青海省制造集团公司的法定代表人是谁？",
        "青海省制造集团公司有哪些分支机构？",
        "苏州贸易有限公司的董事长是谁？",
        "黄丽娟担任了哪些公司的法定代表人？",
        "她还担任了哪些职位？",
        "江苏省制造有限公司三度以内的投资关系，一共关联出了哪些公司？",
        "江苏省制造有限公司三度以内的投资关系，一共关联出了哪些公司？给出公司名单和完整的路径关系。"
    ]
    for q in questions:
        print(f"\n用户问题: {q}")
        res = agent.query(q)
        print("Cypher查询:", res['cypher'])
        print("查询结果:", res['result']) 

def clean_cypher(cypher: str) -> str:
    cypher = cypher.strip()
    cypher = re.sub(r'^```[a-zA-Z]*\\n?', '', cypher)
    cypher = re.sub(r'\\n?```$', '', cypher)
    if cypher.lower().startswith('cypher'):
        cypher = cypher[6:].strip()
    return cypher 

def render_mermaid_in_response(response_text):
    """检测并渲染Mermaid代码块"""
    import re
    
    # 检测Mermaid代码块
    mermaid_pattern = r'```mermaid\s*\n(.*?)\n```'
    matches = re.findall(mermaid_pattern, response_text, re.DOTALL)
    
    if matches:
        # 替换为HTML渲染
        for i, mermaid_code in enumerate(matches):
            html_mermaid = f'''
            <div class="mermaid" id="mermaid-{i}">
            {mermaid_code}
            </div>
            <script>
            mermaid.initialize({{startOnLoad: true}});
            mermaid.init(undefined, "#mermaid-{i}");
            </script>
            '''
            response_text = response_text.replace(f'```mermaid\n{mermaid_code}\n```', html_mermaid)
    
    return response_text 