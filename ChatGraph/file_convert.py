# -*- coding: utf-8 -*-
import os
import sys
import pypandoc


def convert_md_to_docx(input_file='README.md', output_file='README.docx'):
    """
    将 Markdown 文件转换为 Word 文档
    
    Args:
        input_file (str): 输入的 Markdown 文件路径
        output_file (str): 输出的 Word 文档路径
    """

    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 找不到输入文件 '{input_file}'")
        sys.exit(1)

    try:
        # 使用 pypandoc 进行转换
        output = pypandoc.convert_file(
            input_file,
            'docx',
            outputfile=output_file,
            extra_args=['--reference-doc=default.docx'] if os.path.exists('default.docx') else []
        )

        print(f"成功将 '{input_file}' 转换为 '{output_file}'")

    except RuntimeError as e:
        print(f"转换过程中出现错误: {e}")
        print("请确保已安装 pandoc:")
        print("  Windows: choco install pandoc 或从 https://github.com/jgm/pandoc/releases 下载安装")
        print("  macOS: brew install pandoc")
        print("  Linux: sudo apt-get install pandoc")
        sys.exit(1)
    except Exception as e:
        print(f"发生未预期的错误: {e}")
        sys.exit(1)


def main():
    """主函数"""
    # 获取命令行参数
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'README.md'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'README.docx'

    print(f"正在将 '{input_file}' 转换为 '{output_file}'...")
    convert_md_to_docx(input_file, output_file)


if __name__ == '__main__':
    main()
