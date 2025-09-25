#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用MHTML文件解析器
专门用于解析腾讯元宝等网站保存的MHTML聊天记录文件

作者: Claude Code
创建时间: 2025-09-26
功能: 提取MHTML文件中的对话内容，支持中文编码解析
"""

import re
import email
import quopri
import urllib.parse
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import html
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatMessage:
    """聊天消息数据类"""
    sender: str  # 发送者 (user/assistant)
    content: str  # 消息内容
    timestamp: Optional[str] = None
    thinking: Optional[str] = None  # AI思考过程


@dataclass
class ChatSession:
    """聊天会话数据类"""
    title: str
    url: str
    messages: List[ChatMessage]
    created_time: Optional[str] = None


class MHTMLParser:
    """MHTML文件解析器"""

    def __init__(self):
        self.encoding_patterns = {
            # URL编码模式 (=E5=A5=BD 格式)
            'quoted_printable': re.compile(r'=([0-9A-F]{2})', re.IGNORECASE),
            # HTML实体编码
            'html_entities': re.compile(r'&[a-zA-Z][a-zA-Z0-9]*;|&#[0-9]+;|&#x[0-9a-fA-F]+;'),
            # 中文字符模式
            'chinese_chars': re.compile(r'[\u4e00-\u9fff]+'),
        }

        # 腾讯元宝聊天内容特征模式
        self.chat_patterns = {
            'message_container': re.compile(r'hyc-content-md.*?</div>', re.DOTALL | re.IGNORECASE),
            'thinking_process': re.compile(r'已深度思考.*?</div>', re.DOTALL | re.IGNORECASE),
            'user_message': re.compile(r'user.*?assistant', re.DOTALL | re.IGNORECASE),
        }

    def decode_quoted_printable(self, text: str) -> str:
        """解码quoted-printable编码的文本"""
        try:
            # 使用quopri库解码
            decoded_bytes = quopri.decodestring(text.encode('ascii'))
            return decoded_bytes.decode('utf-8', errors='ignore')
        except Exception:
            # 手动解码 =XX 格式
            def replace_hex(match):
                try:
                    hex_value = match.group(1)
                    return chr(int(hex_value, 16))
                except ValueError:
                    return match.group(0)

            return self.encoding_patterns['quoted_printable'].sub(replace_hex, text)

    def decode_html_entities(self, text: str) -> str:
        """解码HTML实体"""
        return html.unescape(text)

    def clean_html_tags(self, text: str) -> str:
        """清理HTML标签"""
        # 移除HTML标签但保留内容
        tag_pattern = re.compile(r'<[^>]+>')
        return tag_pattern.sub('', text)

    def extract_text_content(self, html_content: str) -> str:
        """从HTML内容中提取纯文本"""
        # 先解码quoted-printable
        decoded = self.decode_quoted_printable(html_content)
        # 再解码HTML实体
        decoded = self.decode_html_entities(decoded)
        # 清理HTML标签
        cleaned = self.clean_html_tags(decoded)
        # 清理多余空白
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def parse_mhtml_file(self, file_path: str) -> ChatSession:
        """解析MHTML文件"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 解析MIME结构
        msg = email.message_from_string(content)

        # 提取基本信息
        session_info = self._extract_session_info(msg)

        # 提取HTML内容
        html_content = self._extract_html_content(msg)

        # 解析聊天消息
        messages = self._parse_chat_messages(html_content)

        return ChatSession(
            title=session_info['title'],
            url=session_info['url'],
            messages=messages,
            created_time=session_info['created_time']
        )

    def _extract_session_info(self, msg: email.message.Message) -> Dict:
        """提取会话基本信息"""
        # 提取标题
        subject = msg.get('Subject', '')
        title = self.decode_quoted_printable(subject) if subject else "未知对话"

        # 提取URL
        url = msg.get('Snapshot-Content-Location', '')

        # 提取创建时间
        date = msg.get('Date', '')

        return {
            'title': title,
            'url': url,
            'created_time': date
        }

    def _extract_html_content(self, msg: email.message.Message) -> str:
        """提取HTML内容"""
        html_content = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/html':
                    html_content = part.get_payload()
                    break
        else:
            html_content = msg.get_payload()

        return html_content

    def _parse_chat_messages(self, html_content: str) -> List[ChatMessage]:
        """解析聊天消息"""
        messages = []

        # 先解码整个HTML内容
        decoded_html = self.extract_text_content(html_content)

        # 使用多种策略提取消息
        messages.extend(self._extract_by_patterns(decoded_html))
        messages.extend(self._extract_by_keywords(decoded_html))

        # 去重和排序
        unique_messages = self._deduplicate_messages(messages)

        return unique_messages

    def _extract_by_patterns(self, content: str) -> List[ChatMessage]:
        """基于模式匹配提取消息"""
        messages = []

        # 查找思考过程
        thinking_matches = re.findall(r'已深度思考.*?(\d+秒)', content)
        thinking_content = None
        if thinking_matches:
            thinking_content = f"深度思考（用时{thinking_matches[0]}）"

        # 分割对话段落
        paragraphs = re.split(r'\n\s*\n', content)

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if len(paragraph) < 10:  # 跳过太短的段落
                continue

            # 检测是否为有效对话内容
            if self._is_valid_message(paragraph):
                # 简单启发式判断发送者
                if any(keyword in paragraph for keyword in ['用户', '请', '帮我', '我需要']):
                    sender = 'user'
                else:
                    sender = 'assistant'

                messages.append(ChatMessage(
                    sender=sender,
                    content=paragraph,
                    thinking=thinking_content if sender == 'assistant' else None
                ))

        return messages

    def _extract_by_keywords(self, content: str) -> List[ChatMessage]:
        """基于关键词提取消息"""
        messages = []

        # 查找特定的对话标记
        user_keywords = ['用户提问', '用户问题', '用户需求', '用户确认']
        assistant_keywords = ['AI回应', 'AI分析', 'AI深度分析']

        lines = content.split('\n')
        current_message = []
        current_sender = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测发送者切换
            new_sender = None
            if any(keyword in line for keyword in user_keywords):
                new_sender = 'user'
            elif any(keyword in line for keyword in assistant_keywords):
                new_sender = 'assistant'

            if new_sender and new_sender != current_sender:
                # 保存之前的消息
                if current_message and current_sender:
                    content_text = '\n'.join(current_message).strip()
                    if self._is_valid_message(content_text):
                        messages.append(ChatMessage(
                            sender=current_sender,
                            content=content_text
                        ))

                # 开始新消息
                current_sender = new_sender
                current_message = [line]
            else:
                current_message.append(line)

        # 处理最后一条消息
        if current_message and current_sender:
            content_text = '\n'.join(current_message).strip()
            if self._is_valid_message(content_text):
                messages.append(ChatMessage(
                    sender=current_sender,
                    content=content_text
                ))

        return messages

    def _is_valid_message(self, text: str) -> bool:
        """判断是否为有效的聊天消息"""
        # 长度检查
        if len(text) < 5 or len(text) > 10000:
            return False

        # 包含中文字符
        if not self.encoding_patterns['chinese_chars'].search(text):
            return False

        # 排除明显的HTML/CSS内容
        if any(keyword in text.lower() for keyword in [
            'stylesheet', 'javascript', 'css-', 'class=', 'href=', 'svg', 'xml'
        ]):
            return False

        return True

    def _deduplicate_messages(self, messages: List[ChatMessage]) -> List[ChatMessage]:
        """去重消息"""
        seen = set()
        unique_messages = []

        for msg in messages:
            # 使用内容的前100个字符作为去重键
            key = msg.content[:100]
            if key not in seen:
                seen.add(key)
                unique_messages.append(msg)

        return unique_messages

    def export_to_markdown(self, session: ChatSession, output_path: str = None) -> str:
        """导出为Markdown格式"""
        if output_path is None:
            output_path = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        markdown_content = f"""# {session.title}

**来源**: {session.url}
**创建时间**: {session.created_time}
**消息数量**: {len(session.messages)}

---

"""

        for i, msg in enumerate(session.messages, 1):
            sender_label = "🧑 用户" if msg.sender == 'user' else "🤖 AI助手"

            markdown_content += f"## {i}. {sender_label}\n\n"

            if msg.thinking:
                markdown_content += f"*{msg.thinking}*\n\n"

            markdown_content += f"{msg.content}\n\n---\n\n"

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return output_path

    def export_to_json(self, session: ChatSession, output_path: str = None) -> str:
        """导出为JSON格式"""
        if output_path is None:
            output_path = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # 转换为可序列化的字典
        session_dict = {
            'title': session.title,
            'url': session.url,
            'created_time': session.created_time,
            'messages': [
                {
                    'sender': msg.sender,
                    'content': msg.content,
                    'thinking': msg.thinking,
                    'timestamp': msg.timestamp
                }
                for msg in session.messages
            ]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(session_dict, f, ensure_ascii=False, indent=2)

        return output_path


def main():
    """命令行使用示例"""
    import argparse

    parser = argparse.ArgumentParser(description='MHTML文件解析器')
    parser.add_argument('input_file', help='输入的MHTML文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', '-f', choices=['markdown', 'json'],
                       default='markdown', help='输出格式')

    args = parser.parse_args()

    # 创建解析器实例
    parser_instance = MHTMLParser()

    try:
        # 解析文件
        print(f"正在解析文件: {args.input_file}")
        session = parser_instance.parse_mhtml_file(args.input_file)

        print(f"解析完成!")
        print(f"对话标题: {session.title}")
        print(f"消息数量: {len(session.messages)}")

        # 导出结果
        if args.format == 'markdown':
            output_file = parser_instance.export_to_markdown(session, args.output)
        else:
            output_file = parser_instance.export_to_json(session, args.output)

        print(f"结果已导出到: {output_file}")

    except Exception as e:
        print(f"解析失败: {e}")


if __name__ == "__main__":
    main()