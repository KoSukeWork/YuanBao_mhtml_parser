# MHTML聊天记录解析器

一个专门用于解析腾讯元宝等AI聊天网站保存的MHTML文件的Python工具，能够提取对话内容并导出为可读格式。

## 🚀 功能特性

- ✅ **完整MHTML解析**：支持解析标准MHTML文件格式
- ✅ **中文编码处理**：自动处理quoted-printable编码和HTML实体
- ✅ **智能内容提取**：识别并提取对话消息，区分用户和AI回复
- ✅ **多种导出格式**：支持Markdown和JSON格式导出
- ✅ **思考过程提取**：支持提取AI的思考过程信息
- ✅ **去重和清理**：自动去除重复内容和HTML标签
- ✅ **命令行支持**：提供简单易用的命令行界面

## 📦 安装要求

- Python 3.7+
- 无需额外依赖，使用Python标准库

## 🛠️ 使用方法

### 1. 命令行使用

```bash
# 基本用法 - 解析MHTML文件并导出为Markdown
python mhtml_parser.py your_chat_file.mhtml

# 指定输出文件
python mhtml_parser.py your_chat_file.mhtml -o output.md

# 导出为JSON格式
python mhtml_parser.py your_chat_file.mhtml -f json -o output.json
```

### 2. Python代码使用

```python
from mhtml_parser import MHTMLParser

# 创建解析器实例
parser = MHTMLParser()

# 解析MHTML文件
session = parser.parse_mhtml_file('your_chat_file.mhtml')

# 查看解析结果
print(f"对话标题: {session.title}")
print(f"消息数量: {len(session.messages)}")

# 遍历消息
for msg in session.messages:
    print(f"{msg.sender}: {msg.content[:100]}...")

# 导出为Markdown
markdown_file = parser.export_to_markdown(session, 'output.md')

# 导出为JSON
json_file = parser.export_to_json(session, 'output.json')
```

## 📋 API文档

### MHTMLParser类

主要的解析器类，提供完整的MHTML解析功能。

#### 方法

**`parse_mhtml_file(file_path: str) -> ChatSession`**
- 解析MHTML文件并返回聊天会话对象
- 参数：`file_path` - MHTML文件路径
- 返回：`ChatSession` 对象

**`export_to_markdown(session: ChatSession, output_path: str = None) -> str`**
- 导出为Markdown格式
- 参数：
  - `session` - 聊天会话对象
  - `output_path` - 输出文件路径（可选）
- 返回：输出文件路径

**`export_to_json(session: ChatSession, output_path: str = None) -> str`**
- 导出为JSON格式
- 参数：
  - `session` - 聊天会话对象
  - `output_path` - 输出文件路径（可选）
- 返回：输出文件路径

### 数据结构

#### ChatMessage类
```python
@dataclass
class ChatMessage:
    sender: str          # 发送者 ('user' 或 'assistant')
    content: str         # 消息内容
    timestamp: str       # 时间戳（可选）
    thinking: str        # AI思考过程（可选）
```

#### ChatSession类
```python
@dataclass
class ChatSession:
    title: str                    # 对话标题
    url: str                      # 原始URL
    messages: List[ChatMessage]   # 消息列表
    created_time: str             # 创建时间（可选）
```

## 🎯 使用示例

### 示例1：基本解析

```python
from mhtml_parser import MHTMLParser

parser = MHTMLParser()
session = parser.parse_mhtml_file('game_design_chat.mhtml')

print(f"📋 对话标题: {session.title}")
print(f"🔗 原始链接: {session.url}")
print(f"💬 消息总数: {len(session.messages)}")

# 查看第一条消息
if session.messages:
    first_msg = session.messages[0]
    print(f"\\n第一条消息 ({first_msg.sender}):")
    print(first_msg.content[:200] + "...")
```

### 示例2：过滤特定内容

```python
# 只获取用户消息
user_messages = [msg for msg in session.messages if msg.sender == 'user']
print(f"用户消息数: {len(user_messages)}")

# 只获取AI回复
ai_messages = [msg for msg in session.messages if msg.sender == 'assistant']
print(f"AI回复数: {len(ai_messages)}")

# 查找包含特定关键词的消息
game_related = [msg for msg in session.messages if '游戏' in msg.content]
print(f"游戏相关消息: {len(game_related)}")
```

### 示例3：自定义导出

```python
# 自定义Markdown导出
def custom_export(session: ChatSession, output_file: str):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {session.title}\\n\\n")

        for i, msg in enumerate(session.messages, 1):
            emoji = "🧑" if msg.sender == 'user' else "🤖"
            f.write(f"## {i}. {emoji} {msg.sender}\\n\\n")
            f.write(f"{msg.content}\\n\\n---\\n\\n")

custom_export(session, 'custom_output.md')
```

## 🔧 高级配置

### 自定义解析规则

```python
class CustomMHTMLParser(MHTMLParser):
    def _is_valid_message(self, text: str) -> bool:
        # 自定义消息验证逻辑
        if len(text) < 10:  # 最短长度
            return False

        # 自定义关键词过滤
        if any(keyword in text for keyword in ['广告', '推广']):
            return False

        return super()._is_valid_message(text)

# 使用自定义解析器
custom_parser = CustomMHTMLParser()
session = custom_parser.parse_mhtml_file('chat.mhtml')
```

## 🚨 故障排除

### 常见问题

**Q: 解析后没有提取到内容？**
A: 检查以下几点：
- 确认文件是MHTML格式
- 文件是否损坏或不完整
- 尝试调整 `_is_valid_message` 方法的验证条件

**Q: 中文显示乱码？**
A: 检查：
- 文件编码是否正确
- 使用UTF-8编码保存输出文件

**Q: 解析速度较慢？**
A: 对于大文件：
- 文件较大时解析需要时间
- 可以考虑分段处理或优化正则表达式

### 调试模式

```python
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

parser = MHTMLParser()
session = parser.parse_mhtml_file('chat.mhtml')
```

## 📄 支持的文件格式

- ✅ 腾讯元宝聊天记录 (.mhtml)
- ✅ Chrome/Edge保存的网页 (.mhtml)
- ✅ 其他符合MHTML标准的文件

## 🔄 更新日志

### v1.0.0 (2025-09-26)
- 初始发布
- 支持基本MHTML解析
- 支持中文编码处理
- 支持Markdown和JSON导出
- 提供命令行界面

## 📝 许可证

本项目基于MIT许可证开源。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工具！

## 📧 联系方式

如有问题或建议，请通过GitHub Issues联系。