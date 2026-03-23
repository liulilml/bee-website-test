#!/usr/bin/env node
/**
 * 尝试用用户身份创建飞书文档
 * 如果用户未授权，应该会自动触发授权卡片
 */

const http = require('http');

// 网关地址
const GATEWAY_URL = 'http://127.0.0.1:18789';

// 文档参数
const docParams = {
  title: "验证权限转移（用户所有权）",
  markdown: `欢迎使用飞书文档！

这是一个用于验证权限转移的测试文档。

---

## 📋 文档信息

- **创建时间**：2026-03-15
- **文档用途**：权限验证测试
- **所在位置**：个人空间根目录

---

## ✅ 验证项目

1. 文档创建权限
2. 用户所有权确认
3. 个人空间写入能力

---

*此文档由系统自动创建*`
};

console.log('正在尝试创建文档...');
console.log('标题:', docParams.title);

// 尝试通过网关调用工具
const options = {
  hostname: '127.0.0.1',
  port: 18789,
  path: '/api/tools/call',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  }
};

const req = http.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => { data += chunk; });
  res.on('end', () => {
    console.log('响应状态:', res.statusCode);
    console.log('响应内容:', data);
  });
});

req.on('error', (e) => {
  console.log('请求错误:', e.message);
});

req.write(JSON.stringify({
  tool: 'feishu_create_doc',
  params: docParams
}));

req.end();

console.log('请求已发送，等待响应...');
