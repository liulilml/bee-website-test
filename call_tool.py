#!/usr/bin/env python3
import asyncio
import websockets
import json
import hmac
import hashlib
import base64
import time

async def call_tool():
    uri = "ws://127.0.0.1:18789"
    token = "7604c5346e515c5ccba37658a0f06b384e8e2ad24b6055b1"
    
    markdown_content = """# 欢迎使用飞书文档

这是一篇用于验证权限转移功能的测试文档。

---

## 📋 测试说明

本文档用于测试飞书文档创建和权限管理功能。

### 测试目标

- 验证文档创建功能是否正常工作
- 测试权限转移流程
- 确认 auto-auth 自动授权机制

### 操作步骤

1. 确认文档已成功创建
2. 检查文档访问权限
3. 验证权限转移流程

---

## ✅ 验证清单

- [ ] 文档创建成功
- [ ] 文档可正常访问
- [ ] 权限设置正确
- [ ] 授权流程正常

---

## 📝 备注

如果创建过程中遇到权限不足的错误，系统会自动发起 OAuth 授权流程。

**创建时间**：2026-03-15"""

    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "feishu_create_doc",
            "arguments": {
                "title": "验证权限转移",
                "markdown": markdown_content
            }
        },
        "id": 1
    }
    
    try:
        async with websockets.connect(uri) as ws:
            # Wait for challenge
            msg = await ws.recv()
            data = json.loads(msg)
            print(f"Received: {data}")
            
            if data.get('type') == 'event' and data.get('event') == 'connect.challenge':
                nonce = data['payload']['nonce']
                ts = data['payload']['ts']
                print(f"Challenge: nonce={nonce}, ts={ts}")
                
                # Build authentication payload
                # Sign the nonce with the token
                signature = hmac.new(
                    token.encode(),
                    nonce.encode(),
                    hashlib.sha256
                ).hexdigest()
                
                # Send connect message with auth
                connect_msg = {
                    "type": "connect",
                    "payload": {
                        "token": token,
                        "nonce": nonce,
                        "signature": signature,
                        "role": "operator",
                        "scopes": ["operator.admin"],
                        "platform": "linux",
                        "signedAtMs": int(time.time() * 1000)
                    }
                }
                await ws.send(json.dumps(connect_msg))
                print("Sent connect message")
                
                # Wait for connect response
                response = await ws.recv()
                print(f"Connect response: {response}")
                
                # Now send the tool call
                await ws.send(json.dumps(request))
                print("Sent tool call")
                
                # Wait for response
                result = await ws.recv()
                print(f"Tool response: {result}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(call_tool())
