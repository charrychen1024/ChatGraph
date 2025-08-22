import requests
import json
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import pandas as pd

def neo4j_query_example():
    """
    使用requests.post方式查询Neo4j数据库的示例
    Neo4j HTTP API端点: http://localhost:7474/db/neo4j/tx/commit
    """
    
    # Neo4j HTTP端点URL
    # 注意：需要使用HTTP端口(7474)而非Bolt端口(7687)
    url = "http://192.168.57.150:7474/db/neo4j/tx/commit"
    
    # 查询语句示例
    # query = """
    # MATCH (n) RETURN n LIMIT 10
    # """
    query = """
    MATCH (p:Person {name: "陈建"})-[r]->(c:Company) RETURN p.name as 姓名, c.name AS 公司名称, c.credit_code AS 统一社会信用代码, type(r) as 关系类型
    """
    
    # 构造请求数据
    data = {
        "statements": [
            {
                "statement": query,
                "resultDataContents": ["row", "graph"]
            }
        ]
    }
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # 发送POST请求
    response = requests.post(
        url,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
        headers=headers,
        data=json.dumps(data)
    )
    
    # 处理响应
    if response.status_code == 200:
        result = response.json()
        print("查询成功:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    else:
        print(f"查询失败，状态码: {response.status_code}")
        print(response.text)
        return None

def neo4j_create_example():
    """
    使用requests.post方式在Neo4j中创建节点的示例
    """
    
    url = "http://localhost:7474/db/neo4j/tx/commit"
    
    # 创建节点的Cypher语句
    query = """
    CREATE (p:Person {name: $name, age: $age, city: $city})
    RETURN p
    """
    
    # 构造请求数据
    data = {
        "statements": [
            {
                "statement": query,
                "parameters": {
                    "name": "张三",
                    "age": 30,
                    "city": "北京"
                },
                "resultDataContents": ["row", "graph"]
            }
        ]
    }
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # 发送POST请求
    response = requests.post(
        url,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
        headers=headers,
        data=json.dumps(data)
    )
    
    # 处理响应
    if response.status_code == 200:
        result = response.json()
        print("创建节点成功:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    else:
        print(f"创建节点失败，状态码: {response.status_code}")
        print(response.text)
        return None
    

def parse_neo4j_response_to_dataframe(response_body):
    """
    将Neo4j HTTP API返回的JSON结果解析为pandas DataFrame
    
    Args:
        response_body (str or dict): Neo4j API返回的响应体
        
    Returns:
        pandas.DataFrame: 解析后的数据框
    """
    # 如果是字符串则解析为字典
    if isinstance(response_body, str):
        data = json.loads(response_body)
    else:
        data = response_body
    
    # 提取数据
    results = data.get('results', [])
    if not results:
        return pd.DataFrame()
    
    # 获取第一个结果集的数据
    result_data = results[0].get('data', [])
    columns = results[0].get('columns', [])
    
    # 解析行数据
    rows = []
    for item in result_data:
        # 从row字段获取节点属性数据
        node_data = item.get('row', [{}])
        rows.append(node_data)
    
    # 转换为DataFrame
    df = pd.DataFrame(rows, columns=columns)
    return df
   

def parse_neo4j_response_to_json(response_body):
    """
    解析Neo4j返回的JSON结果，提取数据并转换为列表字典格式
    
    参数:
        response_body: Neo4j返回的JSON数据（字典形式）
    
    返回:
        list: 包含字典的列表，每个字典对应一条记录
    """

    # 如果是字符串则解析为字典
    if isinstance(response_body, str):
        data = json.loads(response_body)
    else:
        data = response_body
    
    # 提取数据
    results = data.get('results', [])
    if not results:
        return pd.DataFrame()
    
    # 获取第一个结果集的数据
    result_data = results[0].get('data', [])
    columns = results[0].get('columns', [])

    # 初始化结果列表
    result_list = []
    
    # 遍历每一行数据
    for row_data in result_data:
        # 创建当前行的字典
        row_dict = {}
        # 将列名与对应的值关联起来
        for i, column in enumerate(columns):
            row_dict[column] = row_data["row"][i]
        # 添加到结果列表
        result_list.append(row_dict)
    
    return result_list

if __name__ == "__main__":
    print("=== Neo4j 查询示例 ===")
    response_body = neo4j_query_example()
    
    # print("\n=== Neo4j 创建节点示例 ===")
    # neo4j_create_example()

    # 结果解析
    # 解析为DataFrame
    df = parse_neo4j_response_to_dataframe(response_body)
    print("解析后的DataFrame:")
    print(df)
    print("\nDataFrame信息:")
    print(df.info())

    # 解析为JSON
    json_data = parse_neo4j_response_to_json(response_body)
    print("解析后的JSON数据:")
    print(json_data)
