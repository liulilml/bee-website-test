#!/usr/bin/env node
/**
 * 生成飞书 OAuth 授权链接
 */

const APP_ID = 'cli_a93cdec73eb8dbd7';

// 需要的权限范围
const SCOPES = [
  'docx:document',
  'docx:document:create',
  'wiki:wiki',
  'drive:file'
].join(',');

// 飞书 OAuth 授权页面 URL
const authUrl = `https://open.feishu.cn/app-redirect?app_id=${APP_ID}&scope=${encodeURIComponent(SCOPES)}`;

console.log('\n📱 飞书文档权限授权链接\n');
console.log('请点击以下链接进行授权：\n');
console.log(authUrl);
console.log('\n');
console.log('授权步骤：');
console.log('1. 点击上面的链接');
console.log('2. 在飞书中确认授权');
console.log('3. 授权完成后告诉我，我就可以用你的身份创建文档了！');
console.log('\n');
