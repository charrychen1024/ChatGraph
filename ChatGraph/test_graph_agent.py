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
        "她还担任了哪些职位？"
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