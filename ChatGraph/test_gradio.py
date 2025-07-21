#!/usr/bin/env python3
"""
测试 Gradio 应用是否能正常启动
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有必要的模块是否能正常导入"""
    try:
        import gradio as gr
        print("✓ gradio 导入成功")
        
        from graph_agent import GraphNLPAgent
        print("✓ GraphNLPAgent 导入成功")
        
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_agent_initialization():
    """测试 Agent 是否能正常初始化"""
    try:
        from graph_agent import GraphNLPAgent
        agent = GraphNLPAgent()
        print("✓ GraphNLPAgent 初始化成功")
        return True
    except Exception as e:
        print(f"✗ Agent 初始化失败: {e}")
        return False

def test_stream_query():
    """测试流式查询功能"""
    try:
        from graph_agent import GraphNLPAgent
        agent = GraphNLPAgent()
        
        # 测试一个简单的问题
        question = "测试问题"
        stream = agent.stream_query(question)
        
        # 检查是否返回生成器
        if hasattr(stream, '__iter__'):
            print("✓ stream_query 返回生成器成功")
            return True
        else:
            print("✗ stream_query 未返回生成器")
            return False
    except Exception as e:
        print(f"✗ 流式查询测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试 Gradio 应用...")
    print("=" * 50)
    
    tests = [
        ("模块导入测试", test_imports),
        ("Agent 初始化测试", test_agent_initialization),
        ("流式查询测试", test_stream_query),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！可以启动 Gradio 应用")
        print("\n启动命令:")
        print("python gradio_app.py")
    else:
        print("✗ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main() 