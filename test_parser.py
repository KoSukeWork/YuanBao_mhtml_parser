#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHTML解析器测试文件
用于测试和验证解析器功能
"""

import unittest
import tempfile
import os
from pathlib import Path
from mhtml_parser import MHTMLParser, ChatMessage, ChatSession


class TestMHTMLParser(unittest.TestCase):
    """MHTML解析器测试类"""

    def setUp(self):
        """测试前准备"""
        self.parser = MHTMLParser()

    def test_decode_quoted_printable(self):
        """测试quoted-printable解码"""
        # 测试中文编码
        encoded_text = "=E4=BD=A0=E5=A5=BD"  # "你好"
        decoded = self.parser.decode_quoted_printable(encoded_text)
        self.assertEqual(decoded, "你好")

        # 测试英文
        encoded_text = "Hello=20World"  # "Hello World"
        decoded = self.parser.decode_quoted_printable(encoded_text)
        self.assertEqual(decoded, "Hello World")

    def test_decode_html_entities(self):
        """测试HTML实体解码"""
        # 测试常见HTML实体
        html_text = "&lt;div&gt;Hello &amp; World&lt;/div&gt;"
        decoded = self.parser.decode_html_entities(html_text)
        self.assertEqual(decoded, "<div>Hello & World</div>")

        # 测试数字实体
        html_text = "&#20320;&#22909;"  # 你好
        decoded = self.parser.decode_html_entities(html_text)
        self.assertEqual(decoded, "你好")

    def test_clean_html_tags(self):
        """测试HTML标签清理"""
        html_content = "<div class='test'>Hello <span>World</span></div>"
        cleaned = self.parser.clean_html_tags(html_content)
        self.assertEqual(cleaned, "Hello World")

    def test_extract_text_content(self):
        """测试文本内容提取"""
        html_content = "<div>=E4=BD=A0=E5=A5=BD &lt;World&gt;</div>"
        extracted = self.parser.extract_text_content(html_content)
        self.assertIn("你好", extracted)
        self.assertIn("<World>", extracted)

    def test_is_valid_message(self):
        """测试消息有效性判断"""
        # 有效消息
        valid_msg = "这是一个有效的中文消息，内容足够长"
        self.assertTrue(self.parser._is_valid_message(valid_msg))

        # 无效消息 - 太短
        invalid_short = "短"
        self.assertFalse(self.parser._is_valid_message(invalid_short))

        # 无效消息 - 没有中文
        invalid_no_chinese = "This is English only message"
        self.assertFalse(self.parser._is_valid_message(invalid_no_chinese))

        # 无效消息 - 包含HTML/CSS
        invalid_html = "这是包含CSS的消息 class='test' stylesheet"
        self.assertFalse(self.parser._is_valid_message(invalid_html))

    def test_deduplicate_messages(self):
        """测试消息去重"""
        messages = [
            ChatMessage("user", "重复消息内容"),
            ChatMessage("assistant", "不同消息内容"),
            ChatMessage("user", "重复消息内容"),  # 重复
            ChatMessage("user", "另一个消息"),
        ]

        deduplicated = self.parser._deduplicate_messages(messages)
        self.assertEqual(len(deduplicated), 3)  # 应该去掉一个重复的

    def test_chat_message_creation(self):
        """测试ChatMessage创建"""
        msg = ChatMessage(
            sender="user",
            content="测试消息内容",
            timestamp="2025-09-26 10:00:00",
            thinking=None
        )

        self.assertEqual(msg.sender, "user")
        self.assertEqual(msg.content, "测试消息内容")
        self.assertEqual(msg.timestamp, "2025-09-26 10:00:00")
        self.assertIsNone(msg.thinking)

    def test_chat_session_creation(self):
        """测试ChatSession创建"""
        messages = [
            ChatMessage("user", "用户消息"),
            ChatMessage("assistant", "AI回复", thinking="思考过程")
        ]

        session = ChatSession(
            title="测试对话",
            url="https://example.com",
            messages=messages,
            created_time="2025-09-26"
        )

        self.assertEqual(session.title, "测试对话")
        self.assertEqual(len(session.messages), 2)
        self.assertEqual(session.messages[1].thinking, "思考过程")

    def test_export_markdown(self):
        """测试Markdown导出"""
        messages = [
            ChatMessage("user", "用户问题"),
            ChatMessage("assistant", "AI回答", thinking="深度思考")
        ]

        session = ChatSession(
            title="测试对话",
            url="https://example.com",
            messages=messages
        )

        # 使用临时文件测试
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            temp_path = f.name

        try:
            output_path = self.parser.export_to_markdown(session, temp_path)
            self.assertEqual(output_path, temp_path)

            # 检查文件内容
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertIn("测试对话", content)
            self.assertIn("用户问题", content)
            self.assertIn("AI回答", content)
            self.assertIn("深度思考", content)

        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_json(self):
        """测试JSON导出"""
        import json

        messages = [
            ChatMessage("user", "用户问题"),
            ChatMessage("assistant", "AI回答")
        ]

        session = ChatSession(
            title="测试对话",
            url="https://example.com",
            messages=messages
        )

        # 使用临时文件测试
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_path = f.name

        try:
            output_path = self.parser.export_to_json(session, temp_path)
            self.assertEqual(output_path, temp_path)

            # 检查文件内容
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.assertEqual(data['title'], "测试对话")
            self.assertEqual(len(data['messages']), 2)
            self.assertEqual(data['messages'][0]['sender'], "user")

        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_parse_nonexistent_file(self):
        """测试解析不存在的文件"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_mhtml_file("nonexistent_file.mhtml")

    def create_test_mhtml_content(self):
        """创建测试用的MHTML内容"""
        return """From: <Saved by Test>
Snapshot-Content-Location: https://test.example.com/chat
Subject: =?utf-8?Q?=E6=B5=8B=E8=AF=95=E5=AF=B9=E8=AF=9D?=
Date: Thu, 26 Sep 2025 10:00:00 +0800
MIME-Version: 1.0
Content-Type: multipart/related;
	type="text/html";
	boundary="----TestBoundary----"


------TestBoundary----
Content-Type: text/html
Content-Transfer-Encoding: quoted-printable

<!DOCTYPE html><html>
<head><meta charset="UTF-8"></head>
<body>
<div class="chat-message">
=E7=94=A8=E6=88=B7=E9=97=AE=E9=A2=98=EF=BC=9A=E4=BD=A0=E5=A5=BD
</div>
<div class="chat-message">
AI=E5=9B=9E=E7=AD=94=EF=BC=9A=E4=BD=A0=E5=A5=BD=EF=BC=8C=E6=88=91=E6=98=AFAI=E5=8A=A9=E6=89=8B
</div>
</body>
</html>

------TestBoundary----"""

    def test_parse_mhtml_content(self):
        """测试解析MHTML内容"""
        # 创建临时MHTML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mhtml', delete=False, encoding='utf-8') as f:
            f.write(self.create_test_mhtml_content())
            temp_path = f.name

        try:
            # 解析文件
            session = self.parser.parse_mhtml_file(temp_path)

            # 验证基本信息
            self.assertIn("测试对话", session.title)
            self.assertEqual(session.url, "https://test.example.com/chat")

            # 验证消息内容
            self.assertGreater(len(session.messages), 0)

        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)


def run_basic_tests():
    """运行基础功能测试"""
    print("🧪 运行MHTML解析器基础测试...")

    # 创建测试套件
    suite = unittest.TestSuite()

    # 添加测试方法
    test_methods = [
        'test_decode_quoted_printable',
        'test_decode_html_entities',
        'test_clean_html_tags',
        'test_extract_text_content',
        'test_is_valid_message',
        'test_deduplicate_messages',
        'test_chat_message_creation',
        'test_chat_session_creation',
        'test_export_markdown',
        'test_export_json',
        'test_parse_nonexistent_file',
        'test_parse_mhtml_content'
    ]

    for method in test_methods:
        suite.addTest(TestMHTMLParser(method))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出结果
    if result.wasSuccessful():
        print("\\n✅ 所有测试通过！")
    else:
        print(f"\\n❌ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")

    return result.wasSuccessful()


def run_integration_test():
    """运行集成测试"""
    print("\\n🔗 运行集成测试...")

    parser = MHTMLParser()

    # 测试文件路径（请根据实际情况修改）
    test_file = "D:\\Downloads\\12345.mhtml"

    if not Path(test_file).exists():
        print(f"⚠️  集成测试跳过：测试文件不存在 {test_file}")
        print("   请将test_file变量设置为有效的MHTML文件路径")
        return True

    try:
        print(f"📁 正在测试文件: {Path(test_file).name}")

        # 解析文件
        session = parser.parse_mhtml_file(test_file)
        print(f"✅ 解析成功: {len(session.messages)} 条消息")

        # 测试导出
        md_file = parser.export_to_markdown(session, "test_output.md")
        json_file = parser.export_to_json(session, "test_output.json")

        print(f"✅ Markdown导出成功: {md_file}")
        print(f"✅ JSON导出成功: {json_file}")

        # 验证导出文件
        if Path(md_file).exists() and Path(json_file).exists():
            print("✅ 导出文件验证成功")

            # 清理测试文件
            os.unlink(md_file)
            os.unlink(json_file)
            print("🧹 清理测试文件完成")

            return True
        else:
            print("❌ 导出文件验证失败")
            return False

    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 MHTML解析器测试套件")
    print("=" * 50)

    # 运行基础测试
    basic_success = run_basic_tests()

    # 运行集成测试
    integration_success = run_integration_test()

    # 总结
    print("\\n📋 测试总结:")
    print(f"   基础测试: {'✅ 通过' if basic_success else '❌ 失败'}")
    print(f"   集成测试: {'✅ 通过' if integration_success else '❌ 失败'}")

    overall_success = basic_success and integration_success
    print(f"\\n🎯 整体结果: {'✅ 所有测试通过' if overall_success else '❌ 存在测试失败'}")

    return overall_success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)