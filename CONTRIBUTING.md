# 贡献指南

## 开发流程

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 代码规范

### Python
- 遵循 PEP 8
- 使用 type hints
- 使用异步/await

### TypeScript/JavaScript
- 使用 ESLint
- 使用 Prettier
- 组件使用函数式组件

## 测试

### 运行后端测试
```bash
cd backend
pytest
```

### 运行前端测试
```bash
cd frontend
npm run test
```

## 提交信息规范

```
feat: 添加新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 代码重构
test: 测试相关
chore: 构建/工具
```

## 问题反馈

请通过 GitHub Issues 报告bug或提出功能请求。
