#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHTML解析器使用示例
演示如何使用mhtml_parser模块解析聊天记录
"""

from mhtml_parser import MHTMLParser, ChatSession, ChatMessage
import json
from pathlib import Path


def basic_example():
    """基本使用示例"""
    print("=== 基本使用示例 ===")

    # 创建解析器实例
    parser = MHTMLParser()

    # 解析文件（请替换为你的MHTML文件路径）
    file_path = "D:\\Downloads\\12345.mhtml"  # 示例文件路径

    try:
        # 解析MHTML文件
        session = parser.parse_mhtml_file(file_path)

        # 显示基本信息
        print(f"📋 对话标题: {session.title}")
        print(f"🔗 原始链接: {session.url}")
        print(f"⏰ 创建时间: {session.created_time}")
        print(f"💬 消息总数: {len(session.messages)}")

        # 显示消息分布
        user_count = sum(1 for msg in session.messages if msg.sender == 'user')
        ai_count = sum(1 for msg in session.messages if msg.sender == 'assistant')
        print(f"   - 用户消息: {user_count}")
        print(f"   - AI回复: {ai_count}")

        # 显示前几条消息的预览
        print("\\n📝 消息预览:")
        for i, msg in enumerate(session.messages[:3], 1):
            sender_emoji = "🧑" if msg.sender == 'user' else "🤖"
            preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            print(f"   {i}. {sender_emoji} {msg.sender}: {preview}")

    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        print("请将示例文件路径替换为你的MHTML文件路径")
    except Exception as e:
        print(f"❌ 解析失败: {e}")


def export_example():
    """导出功能示例"""
    print("\\n=== 导出功能示例 ===")

    parser = MHTMLParser()
    file_path = "D:\\Downloads\\12345.mhtml"

    try:
        session = parser.parse_mhtml_file(file_path)

        # 导出为Markdown
        md_file = parser.export_to_markdown(session, "chat_export.md")
        print(f"✅ Markdown文件已导出: {md_file}")

        # 导出为JSON
        json_file = parser.export_to_json(session, "chat_export.json")
        print(f"✅ JSON文件已导出: {json_file}")

        # 检查导出文件大小
        md_size = Path(md_file).stat().st_size if Path(md_file).exists() else 0
        json_size = Path(json_file).stat().st_size if Path(json_file).exists() else 0

        print(f"   - Markdown文件大小: {md_size:,} 字节")
        print(f"   - JSON文件大小: {json_size:,} 字节")

    except Exception as e:
        print(f"❌ 导出失败: {e}")


def filter_example():
    """内容过滤示例"""
    print("\\n=== 内容过滤示例 ===")

    parser = MHTMLParser()
    file_path = "D:\\Downloads\\12345.mhtml"

    try:
        session = parser.parse_mhtml_file(file_path)

        # 按发送者分类
        user_messages = [msg for msg in session.messages if msg.sender == 'user']
        ai_messages = [msg for msg in session.messages if msg.sender == 'assistant']

        print(f"👥 用户消息数: {len(user_messages)}")
        print(f"🤖 AI消息数: {len(ai_messages)}")

        # 查找关键词
        keywords = ['游戏', '设计', '开发', '版本']
        for keyword in keywords:
            matching_messages = [msg for msg in session.messages if keyword in msg.content]
            print(f"🔍 包含'{keyword}'的消息: {len(matching_messages)}")

        # 查找最长的消息
        if session.messages:
            longest_msg = max(session.messages, key=lambda x: len(x.content))
            print(f"📏 最长消息: {len(longest_msg.content)} 字符 (来自 {longest_msg.sender})")

        # 查找包含思考过程的消息
        thinking_messages = [msg for msg in session.messages if msg.thinking]
        print(f"🧠 包含思考过程的消息: {len(thinking_messages)}")

    except Exception as e:
        print(f"❌ 过滤失败: {e}")


def custom_processing_example():
    """自定义处理示例"""
    print("\\n=== 自定义处理示例 ===")

    parser = MHTMLParser()
    file_path = "D:\\Downloads\\12345.mhtml"

    try:
        session = parser.parse_mhtml_file(file_path)

        # 生成对话统计报告
        stats = {
            'total_messages': len(session.messages),
            'total_characters': sum(len(msg.content) for msg in session.messages),
            'avg_message_length': 0,
            'user_messages': 0,
            'ai_messages': 0,
            'messages_with_thinking': 0
        }

        if session.messages:
            stats['avg_message_length'] = stats['total_characters'] / stats['total_messages']
            stats['user_messages'] = sum(1 for msg in session.messages if msg.sender == 'user')
            stats['ai_messages'] = sum(1 for msg in session.messages if msg.sender == 'assistant')
            stats['messages_with_thinking'] = sum(1 for msg in session.messages if msg.thinking)

        # 保存统计报告
        with open('chat_stats.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print("📊 对话统计报告:")
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.1f}")
            else:
                print(f"   {key}: {value}")

        print("✅ 统计报告已保存到: chat_stats.json")

        # 创建简化版本的对话记录
        simplified_messages = []
        for msg in session.messages:
            simplified_messages.append({
                'role': msg.sender,
                'content': msg.content[:500],  # 只保留前500字符
                'length': len(msg.content)
            })

        with open('chat_simplified.json', 'w', encoding='utf-8') as f:
            json.dump(simplified_messages, f, ensure_ascii=False, indent=2)

        print("✅ 简化版对话已保存到: chat_simplified.json")

    except Exception as e:
        print(f"❌ 自定义处理失败: {e}")


def batch_processing_example():
    """批量处理示例"""
    print("\\n=== 批量处理示例 ===")

    # 模拟批量处理多个MHTML文件
    mhtml_files = [
        "D:\\Downloads\\12345.mhtml",
        # 可以添加更多文件路径
    ]

    parser = MHTMLParser()
    results = []

    for file_path in mhtml_files:
        try:
            if Path(file_path).exists():
                print(f"🔄 正在处理: {Path(file_path).name}")
                session = parser.parse_mhtml_file(file_path)

                result = {
                    'file': Path(file_path).name,
                    'title': session.title,
                    'message_count': len(session.messages),
                    'url': session.url,
                    'status': 'success'
                }

                # 导出每个文件
                output_name = Path(file_path).stem
                parser.export_to_markdown(session, f"{output_name}_export.md")

                results.append(result)
                print(f"✅ 处理完成: {result['message_count']} 条消息")

            else:
                print(f"⚠️  文件不存在: {file_path}")
                results.append({
                    'file': Path(file_path).name,
                    'status': 'file_not_found'
                })

        except Exception as e:
            print(f"❌ 处理失败: {file_path} - {e}")
            results.append({
                'file': Path(file_path).name,
                'status': 'error',
                'error': str(e)
            })

    # 保存批量处理结果
    with open('batch_processing_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\\n📋 批量处理完成，共处理 {len(mhtml_files)} 个文件")
    success_count = sum(1 for r in results if r.get('status') == 'success')
    print(f"   ✅ 成功: {success_count}")
    print(f"   ❌ 失败: {len(mhtml_files) - success_count}")
    print("✅ 结果报告已保存到: batch_processing_results.json")


def main():
    """主函数 - 运行所有示例"""
    print("🚀 MHTML解析器使用示例")
    print("=" * 50)

    # 运行各种示例
    basic_example()
    export_example()
    filter_example()
    custom_processing_example()
    batch_processing_example()

    print("\\n🎉 所有示例运行完成！")
    print("\\n💡 提示:")
    print("   - 请将示例中的文件路径替换为你的实际MHTML文件路径")
    print("   - 查看生成的输出文件了解解析结果")
    print("   - 可以根据需要修改示例代码")


if __name__ == "__main__":
    main()