#!/usr/bin/env node
/**
 * 创建飞书文档并分享给用户
 */

const APP_ID = 'cli_a93cdec73eb8dbd7';
const APP_SECRET = 'KaFOPmXRCXyicKSrxHxeihNEeAqTCwJd';
const USER_ID = 'ou_8c6d70c1a28c7408f57730dfac0f19c7';

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
      title: '验证权限转移',
      content: [
        {
          block_type: 1,
          heading1: {
            elements: [{ text_run: { text: '验证权限转移' } }]
          }
        },
        {
          block_type: 2,
          text: {
            elements: [{ text_run: { text: '\n本文档用于验证权限转移功能。' } }]
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
  const data = await res.json();
  if (data.code !== 0) {
    throw new Error(`创建文档失败：${data.message}`);
  }
  return data.data.document;
}

async function shareDoc(token, documentId, userId) {
  // 使用文档权限 API 添加协作者
  const res = await fetch(`https://open.feishu.cn/open-apis/docx/v1/documents/${documentId}/permissions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      members: [{
        id: userId,
        id_type: 'open_id',
        permission: 'edit'
      }]
    })
  });
  const text = await res.text();
  console.log('分享响应:', text);
  try {
    const data = JSON.parse(text);
    if (data.code !== 0) {
      console.log('分享失败:', data.message);
    } else {
      console.log('分享成功!');
    }
    return data;
  } catch (e) {
    console.log('响应不是 JSON');
  }
}

async function main() {
  try {
    console.log('正在获取 access token...');
    const token = await getTenantAccessToken();
    
    console.log('正在创建文档...');
    const doc = await createDoc(token);
    console.log('\n✅ 文档创建成功！');
    console.log(`文档 ID: ${doc.document_id}`);
    console.log(`文档 URL: https://www.feishu.cn/docx/${doc.document_id}`);
    
    console.log('\n正在分享文档给用户...');
    await shareDoc(token, doc.document_id, USER_ID);
    console.log('✅ 文档已分享给用户，用户拥有编辑权限！');
    
  } catch (err) {
    console.error('❌ 错误:', err.message);
    process.exit(1);
  }
}

main();
