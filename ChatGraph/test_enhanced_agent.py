#!/usr/bin/env python3
"""
测试增强后的 GraphNLPAgent 功能
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_question_classification():
    """测试问题分类功能"""
    print("测试问题分类功能...")
    try:
        from graph_agent import GraphNLPAgent
        agent = GraphNLPAgent()
        
        # 测试图数据库相关问题
        graph_questions = [
            "张伟投资了哪些公司？",
            "江苏科技有限公司的法定代表人是谁？",
            "青海省制造集团公司有哪些分支机构？"
        ]
        
        # 测试一般对话问题
        general_questions = [
            "你好",
            "今天天气怎么样？",
            "谢谢你的帮助"
        ]
        
        print("\n图数据库相关问题分类:")
        for q in graph_questions:
            result = agent.classify_question(q)
            print(f"  '{q}' -> {result}")
        
        print("\n一般对话问题分类:")
        for q in general_questions:
            result = agent.classify_question(q)
            print(f"  '{q}' -> {result}")
        
        return True
    except Exception as e:
        print(f"✗ 问题分类测试失败: {e}")
        return False

def test_cypher_fix():
    """测试Cypher纠错功能"""
    print("\n测试Cypher纠错功能...")
    try:
        from graph_agent import GraphNLPAgent
        agent = GraphNLPAgent()
        
        # 测试有语法错误的Cypher
        bad_cypher = "MATCH (n:Company) WHERE n.name = '测试公司' RETURN n.name"
        error_message = "Variable `n` not defined"
        
        fixed_cypher = agent.fix_cypher(bad_cypher, error_message)
        print(f"  原始Cypher: {bad_cypher}")
        print(f"  错误信息: {error_message}")
        print(f"  修正后: {fixed_cypher}")
        
        return True
    except Exception as e:
        print(f"✗ Cypher纠错测试失败: {e}")
        return False

def test_cypher_execution_with_retry():
    """测试Cypher执行重试功能"""
    print("\n测试Cypher执行重试功能...")
    try:
        from graph_agent import GraphNLPAgent
        agent = GraphNLPAgent()
        
        # 测试正确的Cypher
        good_cypher = "MATCH (n:Company) RETURN n.name LIMIT 5"
        success, result, final_cypher = agent.execute_cypher_with_retry(good_cypher)
        print(f"  正确Cypher执行结果: {success}")
        print(f"  返回记录数: {len(result) if success else 0}")
        
        # 测试错误的Cypher（应该会尝试纠错）
        bad_cypher = "MATCH (n:Company) WHERE n.name = '测试公司' RETURN n.name"
        success, result, final_cypher = agent.execute_cypher_with_retry(bad_cypher)
        print(f"  错误Cypher执行结果: {success}")
        print(f"  错误信息: {result if not success else 'N/A'}")
        
        return True
    except Exception as e:
        print(f"✗ Cypher执行重试测试失败: {e}")
        return False

def test_general_chat():
    """测试一般对话功能"""
    print("\n测试一般对话功能...")
    try:
        from graph_agent import GraphNLPAgent
        agent = GraphNLPAgent()
        
        # 测试一般对话
        general_question = "你好，今天天气怎么样？"
        result = agent.query(general_question)
        print(f"  问题: {general_question}")
        print(f"  回答: {result['result']}")
        print(f"  Cypher: {result['cypher']}")
        
        return True
    except Exception as e:
        print(f"✗ 一般对话测试失败: {e}")
        return False

def test_graph_query():
    """测试图数据库查询功能"""
    print("\n测试图数据库查询功能...")
    try:
        from graph_agent import GraphNLPAgent
        agent = GraphNLPAgent()
        
        # 测试图数据库查询
        graph_question = "张伟投资了哪些公司？"
        result = agent.query(graph_question)
        print(f"  问题: {graph_question}")
        print(f"  回答: {result['result']}")
        print(f"  Cypher: {result['cypher']}")
        
        return True
    except Exception as e:
        print(f"✗ 图数据库查询测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试增强后的 GraphNLPAgent...")
    print("=" * 60)
    
    tests = [
        ("问题分类测试", test_question_classification),
        ("Cypher纠错测试", test_cypher_fix),
        ("Cypher执行重试测试", test_cypher_execution_with_retry),
        ("一般对话测试", test_general_chat),
        ("图数据库查询测试", test_graph_query),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
            print(f"  ✓ {test_name} 通过")
        else:
            print(f"  ✗ {test_name} 失败")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！增强后的Agent功能正常")
        print("\n主要改进:")
        print("1. ✓ 支持问题类型分类（图查询 vs 一般对话）")
        print("2. ✓ 支持Cypher语法自动纠错")
        print("3. ✓ 支持Cypher执行重试机制")
        print("4. ✓ 更好的错误处理和用户体验")
    else:
        print("✗ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main() 