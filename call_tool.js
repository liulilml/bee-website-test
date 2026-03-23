const WebSocket = require('ws');

const ws = new WebSocket('ws://127.0.0.1:18789');

ws.on('open', () => {
  console.log('Connected to gateway');
  
  // Send tool call request
  const request = {
    jsonrpc: '2.0',
    method: 'tools/call',
    params: {
      name: 'feishu_create_doc',
      arguments: {
        title: '验证权限转移',
        markdown: `# 欢迎使用飞书文档

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

**创建时间**：2026-03-15`
      }
    },
    id: 1
  };
  
  ws.send(JSON.stringify(request));
});

ws.on('message', (data) => {
  console.log('Response:', data.toString());
  ws.close();
});

ws.on('error', (err) => {
  console.error('Error:', err);
  process.exit(1);
});

ws.on('close', () => {
  console.log('Connection closed');
});
