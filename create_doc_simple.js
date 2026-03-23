#!/usr/bin/env node
/**
 * 创建飞书文档 - 测试用户授权流程
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

async function createDoc(token) {
  const res = await fetch('https://open.feishu.cn/open-apis/docx/v1/documents', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      title: '我的飞书文档',
      content: [
        {
          block_type: 1,
          heading1: {
            elements: [{ text_run: { text: '我的飞书文档' } }]
          }
        },
        {
          block_type: 2,
          text: {
            elements: [{ text_run: { text: '\n这是一个测试文档。' } }]
          }
        },
        {
          block_type: 2,
          text: {
            elements: [{ text_run: { text: '\n创建时间：2026-03-15' } }]
          }
        }
      ]
    })
  });
  const text = await res.text();
  console.log('API 响应:', text);
  const data = JSON.parse(text);
  if (data.code !== 0) {
    throw new Error(`创建文档失败：${data.message}`);
  }
  return data.data.document;
}

async function main() {
  try {
    console.log('正在获取 access token...\n');
    const token = await getTenantAccessToken();
    
    console.log('正在创建文档...\n');
    const doc = await createDoc(token);
    
    console.log('\n✅ 文档创建成功！\n');
    console.log('📄 文档 ID:', doc.document_id);
    console.log('🔗 文档 URL: https://www.feishu.cn/docx/' + doc.document_id);
    console.log('\n');
  } catch (err) {
    console.error('\n❌ 错误:', err.message);
    console.log('\n');
    console.log('如果错误提示权限不足，请先在开放平台开通文档权限：');
    console.log('https://open.feishu.cn/app/cli_a93cdec73eb8dbd7/permission');
    console.log('\n');
    process.exit(1);
  }
}

main();
