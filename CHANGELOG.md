# 更新日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [v1.0.0] - 2026-01-27

### 新增
- 🛡️ **备份-回滚机制**：清理前自动备份，出问题可一键恢复
  - 自动选择非C盘剩余空间最大的驱动器存放备份
  - 智能备份格式：小于1GB直接复制，大于1GB压缩
  - 完整的回滚恢复功能
  - 备份管理命令（list/info/delete/cleanup）

### 变更
- 更新工作流程，增加备份和验证阶段
- 更新操作指南，添加备份相关说明
- 新增 FAQ：Q8-Q10 备份相关问题

### 文件变更
- 新增 `backup.py` - 备份恢复核心模块
- 更新 `skill.md` - 工作流程定义
- 更新 `GUIDE.md` - 操作指南
- 更新 `README.md` - 添加版本徽章

---

## [v0.2.0] - 2026-01-26

### 新增
- 临时文件清理功能：清理完成后可选删除扫描数据和清理脚本
- `scan.py --cleanup` 命令

### 改进
- 优化 WizTree 导出参数，设置 `/exportmaxdepth=200` 减小文件大小

---

## [v0.1.0] - 2026-01-25

### 初始版本
- ⚡ WizTree 快速扫描集成
- 🤖 AI 智能分析：识别可清理目录
- 🎯 三级优先级分类（高/中/低）
- 🔒 安全规则：永不删除系统文件
- 🤝 双模式支持：普通权限/管理员权限

### 核心文件
- `scan.py` - 自动扫描脚本
- `analyze.py` - 数据分析脚本
- `skill.md` - Skill 定义
- `GUIDE.md` - 操作指南

---

## 版本规范

- **MAJOR** (主版本号)：不兼容的 API 变更
- **MINOR** (次版本号)：向下兼容的功能新增
- **PATCH** (修订号)：向下兼容的问题修复

[v1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
[v0.2.0]: https://github.com/user/repo/releases/tag/v0.2.0
[v0.1.0]: https://github.com/user/repo/releases/tag/v0.1.0
