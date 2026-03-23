#!/usr/bin/env node
/**
 * 创建飞书文档的脚本
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

async function createDoc(token, title, content) {
  const res = await fetch('https://open.feishu.cn/open-apis/docx/v1/documents', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      title: title,
      content: [
        {
          block_type: 1, // 标题
          heading1: {
            elements: [{ text_run: { text: title } }]
          }
        },
        ...content
      ]
    })
  });
  const text = await res.text();
  console.log('API 响应:', text);
  const data = JSON.parse(text);
  if (data.code !== 0) {
    throw new Error(`创建文档失败：${data.message}`);
  }
  return data.data;
}

async function main() {
  try {
    console.log('正在获取 access token...');
    const token = await getTenantAccessToken();
    
    console.log('正在创建文档...');
    const title = '严重创建权限';
    const content = [
      {
        block_type: 2, // 段落
        text: {
          elements: [{ text_run: { text: '这是一个测试文档，用于验证自建文档创建功能。' } }]
        }
      },
      {
        block_type: 2,
        text: {
          elements: [{ text_run: { text: '\n创建时间：2026-03-15' } }]
        }
      },
      {
        block_type: 2,
        text: {
          elements: [{ text_run: { text: '创建位置：个人知识库' } }]
        }
      }
    ];
    
    const doc = await createDoc(token, title, content);
    console.log('\n✅ 文档创建成功！');
    console.log(`文档 ID: ${doc.document_id}`);
    console.log(`文档 URL: https://www.feishu.cn/docx/${doc.document_id}`);
  } catch (err) {
    console.error('❌ 错误:', err.message);
    process.exit(1);
  }
}

main();
