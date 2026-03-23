// Script to call feishu_create_doc through the plugin API
import { LarkClient } from './extensions/openclaw-lark/src/core/lark-client.js';
import { registerFeishuMcpDocTools } from './extensions/openclaw-lark/src/tools/mcp/doc/index.js';

const markdown = `# 欢迎使用飞书文档

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

**创建时间**：2026-03-15`;

console.log('This approach requires the full OpenClaw runtime API which is not available in a standalone script.');
console.log('The feishu_create_doc tool needs to be called through the agent protocol.');
