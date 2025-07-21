import os
import re
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_community.graphs import Neo4jGraph as Neo4jGraphStore
from langchain.chains import GraphCypherQAChain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import OpenAIEmbeddings, DashScopeEmbeddings
import config

# Set API key environment variable in script
os.environ["OPENAI_API_KEY"] = "sk-086fa9f54d164f1199951bf93c41c4b6"

# 1. 加载schema知识库
schema_path = os.path.join(os.path.dirname(__file__), 'database_schema.md')
loader = TextLoader(schema_path, encoding='utf-8')
docs = loader.load()
text_splitter = MarkdownTextSplitter(chunk_size=800, chunk_overlap=100)
documents = text_splitter.split_documents(docs)
embeddings = DashScopeEmbeddings(
    model='text-embedding-v4',
    dashscope_api_key=os.environ["OPENAI_API_KEY"],
)
vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever()

# 2. 初始化Neo4j工具
neo4j_url = config.NEO4J_URI
neo4j_user = config.NEO4J_USER
neo4j_password = config.NEO4J_PASSWORD
graph = Neo4jGraphStore(
    url=neo4j_url,
    username=neo4j_user,
    password=neo4j_password
)

# 3. 初始化Qwen大模型（用OpenAI API方式）
llm = ChatOpenAI(
    model="deepseek-v3",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=SecretStr(os.environ["OPENAI_API_KEY"]),
    temperature=0.2,
    streaming=True  # 关键参数
)

# 4. 构建Cypher QA链，结合schema知识库
cypher_prompt = PromptTemplate(
    input_variables=["schema", "question", "history"],
    template="""
你是一个企业知识图谱专家，熟练掌握neo4j图数据库的使用方法和cypher语法。
已知图数据库的schema如下：
{schema}
根据schema，你已经掌握了neo4j图数据库的schema，可以熟练使用cypher语法进行查询。
历史对话：{history}
请根据用户问题，生成最合适的Cypher查询语句，并给出简要中文解释。
如果用户问题中包含"公司"、"企业"、"集团"等关键词，请优先使用MATCH (n:Company)进行查询。
如果用户问题中包含"人"、"个人"、"自然人"等关键词，请优先使用MATCH (n:Person)进行查询。
问题：{question}
Cypher:
要求：
1. 确保cypher语句能够正确执行，并且返回结果符合用户预期。
2. 查询结果如果不为空，要根据返回结果整理出用户想要的结果。
3. 如果查询结果为空，请给出简要的中文解释。
4. 重要：当查询返回结果时，请直接基于返回的数据回答用户问题，不要回答"不知道"。
5. 如果查询结果包含具体数据，请用自然语言描述这些数据，例如："查询结果显示，xxx公司有以下几个分支机构：..."
"""
)

# 5. 问题类型判断prompt
question_classifier_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
请判断以下问题是否与图数据库查询相关。如果问题涉及企业、人员、投资关系、分支机构、职位等图数据库中的实体和关系，回答"graph_query"；
如果是问候、闲聊、天气等无关问题，回答"general_chat"。

问题：{question}
类型：
"""
)

# 6. Cypher纠错prompt
cypher_fix_prompt = PromptTemplate(
    input_variables=["cypher", "error_message", "schema"],
    template="""
你是一个Neo4j Cypher语法专家。以下Cypher查询语句执行时出现了错误，请根据错误信息修正语法：

原始Cypher：
{cypher}

错误信息：
{error_message}

图数据库Schema：
{schema}

请修正Cypher语法错误，只返回修正后的Cypher语句，不要包含其他解释：
"""
)

# 4. 只生成Cypher的Prompt
cypher_gen_prompt = PromptTemplate(
    input_variables=["schema", "question", "history"],
    template="""
你是一个企业知识图谱专家，熟练掌握neo4j图数据库的使用方法和cypher语法。
已知图数据库的schema如下：
{schema}
历史对话：{history}
请根据用户问题，生成最合适的Cypher查询语句，只输出Cypher，不要执行，不要解释。
问题：{question}
Cypher:
"""
)

def clean_cypher(cypher: str) -> str:
    cypher = cypher.strip()
    cypher = re.sub(r'^```[a-zA-Z]*\\n?', '', cypher)
    cypher = re.sub(r'\\n?```$', '', cypher)
    if cypher.lower().startswith('cypher'):
        cypher = cypher[6:].strip()
    return cypher

class GraphNLPAgent:
    def __init__(self):
        self.retriever = retriever
        self.schema = docs[0].page_content
        self.memory = ConversationBufferMemory(memory_key="history", return_messages=True)
        self.llm = llm
        self.graph = graph
        self.cypher_gen_prompt = cypher_gen_prompt
        self.question_classifier_prompt = question_classifier_prompt
        self.cypher_fix_prompt = cypher_fix_prompt

    def classify_question(self, question: str) -> str:
        try:
            response = self.llm.invoke(self.question_classifier_prompt.format(question=question))
            result = str(response.content).strip().lower()
            if "graph_query" in result:
                return "graph_query"
            else:
                return "general_chat"
        except:
            return "general_chat"

    def fix_cypher(self, cypher: str, error_message: str) -> str:
        try:
            response = self.llm.invoke(self.cypher_fix_prompt.format(
                cypher=cypher,
                error_message=error_message,
                schema=self.schema
            ))
            return str(response.content).strip()
        except:
            return ""

    def execute_cypher_with_retry(self, cypher: str, max_retries: int = 3) -> tuple:
        for attempt in range(max_retries):
            try:
                records = self.graph.query(cypher)
                return True, records, cypher
            except Exception as e:
                error_message = str(e)
                print(f"Cypher执行错误 (尝试 {attempt + 1}/{max_retries}): {error_message}")
                if attempt < max_retries - 1:
                    fixed_cypher = self.fix_cypher(cypher, error_message)
                    if fixed_cypher and fixed_cypher != cypher:
                        print(f"修正后的Cypher: {fixed_cypher}")
                        cypher = fixed_cypher
                        continue
                if attempt == max_retries - 1:
                    user_tip = (
                        "很抱歉，系统多次尝试修正 Cypher 查询语句仍未成功。"
                        "请尝试换种问法，或联系管理员协助排查。"
                        f"（最后一次错误信息：{error_message}）"
                    )
                    return False, user_tip, cypher
        return False, "达到最大重试次数", cypher

    def query(self, question: str):
        question_type = self.classify_question(question)
        if question_type == "general_chat":
            general_response = self.llm.invoke(f"用户说：{question}\n请用友好的方式回复，不要涉及图数据库查询。")
            return {"result": general_response.content, "cypher": None}
        history = self.memory.load_memory_variables({}).get("history", [])
        history_text = "\n".join([f"用户: {h.content}" if h.type=="human" else f"助手: {h.content}" for h in history])
        related_schema = self.retriever.get_relevant_documents(question)
        schema_text = '\n'.join([d.page_content for d in related_schema]) or self.schema
        # 只生成Cypher
        cypher_response = self.llm.invoke(
            self.cypher_gen_prompt.format(schema=schema_text, question=question, history=history_text)
        )
        cypher = str(cypher_response.content).strip()
        # 去除 markdown 代码块包裹
        cypher = clean_cypher(cypher)
        if cypher.startswith("cypher"):
            cypher = cypher[len("cypher"):].strip()
        if cypher.startswith("```") and cypher.endswith("```"):
            cypher = cypher[3:-3].strip()
        cypher = re.sub(r"^```[a-zA-Z]*\\n|\\n```$", "", cypher).strip()
        # 执行Cypher并处理结果
        if cypher:
            success, query_result, final_cypher = self.execute_cypher_with_retry(cypher)
            if success:
                context = str(query_result)
                response_prompt = f"""
                        基于以下查询结果，回答用户问题：
                        用户问题：{question}
                        查询结果：{context}
                        请用自然语言回答用户问题，如果结果为空，说明没有找到相关信息。
                        """
                response = self.llm.invoke(response_prompt)
                final_result = response.content
                cypher = final_cypher
            else:
                final_result = query_result
                cypher = final_cypher
        else:
            final_result = "未能生成有效的Cypher语句。"
        self.memory.save_context({"input": question}, {"output": str(final_result)})
        return {"result": final_result, "cypher": cypher}

    def stream_query(self, question: str):
        question_type = self.classify_question(question)
        if question_type == "general_chat":
            general_response = self.llm.invoke(f"用户说：{question}\n请用友好的方式回复，不要涉及图数据库查询。")
            yield general_response.content
            return
        history = self.memory.load_memory_variables({}).get("history", [])
        history_text = "\n".join([f"用户: {h.content}" if h.type=="human" else f"助手: {h.content}" for h in history])
        related_schema = self.retriever.get_relevant_documents(question)
        schema_text = '\n'.join([d.page_content for d in related_schema]) or self.schema
        # 只生成Cypher
        cypher_response = self.llm.invoke(
            self.cypher_gen_prompt.format(schema=schema_text, question=question, history=history_text)
        )
        cypher = str(cypher_response.content).strip()
        # 去除 markdown 代码块包裹
        cypher = clean_cypher(cypher)
        if cypher.startswith("cypher"):
            cypher = cypher[len("cypher"):].strip()
        if cypher.startswith("```") and cypher.endswith("```"):
            cypher = cypher[3:-3].strip()
        cypher = re.sub(r"^```[a-zA-Z]*\\n|\\n```$", "", cypher).strip()
        yield f"生成的Cypher:\n{cypher}"
        # 执行Cypher并生成最终回答
        if cypher:
            success, query_result, final_cypher = self.execute_cypher_with_retry(cypher)
            if success:
                context = str(query_result)
                response_prompt = f"""
                    基于以下查询结果，回答用户问题：
                    用户问题：{question}
                    查询结果：{context}
                    请用自然语言回答用户问题，如果结果为空，说明没有找到相关信息。
                    """
                response = self.llm.invoke(response_prompt)
                final_result = response.content
            else:
                final_result = query_result
        else:
            final_result = "未能生成有效的Cypher语句。"
        self.memory.save_context({"input": question}, {"output": str(final_result)})
        yield final_result

