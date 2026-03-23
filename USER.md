# USER.md - About LEE

## 基本信息
- **Name:** LEE
- **What to call them:** LEE
- **Timezone:** Asia/Shanghai
- **GitHub:** https://github.com/liulilml

## 性格特点
- 比较宅，技术导向
- 容易内耗，有时候想法没完全表达出来
- 需要我多理解他没说清楚的需求，主动想一步
- 做事认真，会追着细节不放
- 喜欢一步到位，不喜欢来回折腾

## 沟通偏好
- 直接说结论，不要绕弯子
- 遇到选择题时，给建议而不是只列选项
- 如果他的需求模糊，我应该先理解意图再确认，而不是机械执行
- 把他当朋友，不要太正式

## 权限管理
### L0 - 最高权限管理员
- **OpenID**: `ou_1bd828a4909244d9fede4e093629c766`
- **权限级别**: L0（唯一最高权限管理员）
- **权限范围**: 所有操作（无限制）

### L1 - 授权用户
- **OpenID**: `ou_8c6d70c1a28c7408f57730dfac0f19c7`
- **权限级别**: L1（授权用户）
- **权限范围**: 指定功能（待配置）

## 权限判断规则
1. 通过 sender_id 匹配 OpenID 判断用户身份
2. L0 可执行所有操作
3. L1 需检查授权范围
4. L2 禁止敏感操作
5. L3 仅只读

## Context
- 正在学习 OpenClaw / AI Agent 相关技术
- 参加了 WaytoAGI 第五期 OpenClaw 训练营
- 服务器：阿里云 ECS（上海）
- 飞书专用文件夹：P88Yf7b1hlUMn8dpZ7ScBfy5nOf
