# W1D3 Chat Demo

这是 Week 1 Day 3 的最小聊天 Demo，目标是把“课程里的聊天概念”落到一个可以直接运行的小应用里。

补充阅读：

- [TECHNICAL_DETAILS.md](E:/Learning/working_Content/generative-ai-for-beginners/07-building-chat-applications/python/W1D3/TECHNICAL_DETAILS.md)
- [TECHNICAL_DETAILS_EMBEDDED.html](E:/Learning/working_Content/generative-ai-for-beginners/07-building-chat-applications/python/W1D3/TECHNICAL_DETAILS_EMBEDDED.html)

技术图解：

- [TECHNICAL_DETAILS.md](E:/Learning/working_Content/generative-ai-for-beginners/07-building-chat-applications/python/W1D3/TECHNICAL_DETAILS.md) 中包含 4 张 Excalidraw 风格架构图
- 如果 Markdown 预览无法显示图片，请打开 [TECHNICAL_DETAILS_EMBEDDED.html](E:/Learning/working_Content/generative-ai-for-beginners/07-building-chat-applications/python/W1D3/TECHNICAL_DETAILS_EMBEDDED.html)

## 目录说明

- `app.py`：Flask 后端，提供页面和 `/api/chat` 接口
- `templates/index.html`：聊天前端页面
- `TECHNICAL_DETAILS.md`：给技术小白和中级开发者看的技术说明与架构图

## 功能说明

- 打开页面后可以直接输入消息并发送
- 如果检测到 OpenAI Key，就调用真实模型回复
- 如果没有检测到 Key，就自动切换到本地回退模式，方便先跑通流程

## Key 读取顺序

程序会按下面顺序查找 Key：

1. 环境变量 `OPENAI_API_KEY`
2. `C:\Openaikey`
3. `C:\Openaikey.txt`
4. 其他符合 `C:\Openaikey*` 的文件

## 启动方式

```powershell
cd E:\Learning\working_Content\generative-ai-for-beginners\07-building-chat-applications\python\W1D3
python app.py
```

启动后访问：

`http://127.0.0.1:5055/`

## 接口说明

- `GET /`：聊天页面
- `POST /api/chat`：聊天接口
- `GET /api/chat`：接口说明页

`POST /api/chat` 的请求体示例：

```json
{
  "message": "请解释什么是 few-shot prompting"
}
```

## 后续可扩展方向

- 加入多轮上下文记忆
- 增加系统提示词配置
- 增加错误提示和加载状态
- 增加聊天记录持久化
