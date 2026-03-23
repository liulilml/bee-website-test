#!/usr/bin/env node
/**
 * 直接调用飞书 MCP 工具创建文档
 */

const APP_ID = 'cli_a93cdec73eb8dbd7';
const APP_SECRET = 'KaFOPmXRCXyicKSrxHxeihNEeAqTCwJd';

async function getTenantAccessToken() {
  const res = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ app_id: APP_ID, app_secret: APP_SECRET })
  });
  const data = await res.json();
  if (data.code !== 0) {
    throw new Error(`获取 token 失败：${data.message}`);
  }
  return data.tenant_access_token;
}

async function callMcpTool(token, title, markdown) {
  // 飞书 MCP 端点
  const endpoint = 'https://mcp.feishu.cn/mcp';
  
  const body = {
    jsonrpc: '2.0',
    id: 'create-doc-1',
    method: 'tools/call',
    params: {
      name: 'create-doc',
      arguments: {
        title: title,
        markdown: markdown
      }
    }
  };
  
  const headers = {
    'Content-Type': 'application/json',
    'X-Lark-MCP-UAT': token,
    'X-Lark-MCP-Allowed-Tools': 'create-doc'
  };
  
  const res = await fetch(endpoint, {
    method: 'POST',
    headers,
    body: JSON.stringify(body)
  });
  
  const text = await res.text();
  console.log('MCP 响应:', text);
  
  const data = JSON.parse(text);
  if (data.error) {
    throw new Error(`MCP error: ${data.error.message}`);
  }
  
  return data.result;
}

async function main() {
  try {
    console.log('正在获取 access token...');
    const token = await getTenantAccessToken();
    
    console.log('正在调用 MCP 工具创建文档...');
    const title = '验证权限转移';
    const markdown = `# 欢迎使用飞书文档

本文档用于验证权限转移功能。

## 📋 测试说明

### 测试目标
验证文档创建后所有权归属用户。

### 预期结果
- ✅ 文档创建在个人空间根目录
- ✅ 文档所有权归用户所有

---

**创建时间**：2026-03-15

<callout emoji="💡" background-color="light-blue">
提示：本文档由自动化工具创建，用于权限验证测试。
</callout>`;
    
    const result = await callMcpTool(token, title, markdown);
    console.log('\n✅ 文档创建成功！');
    console.log('结果:', JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('❌ 错误:', err.message);
    process.exit(1);
  }
}

main();
