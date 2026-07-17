# 更新日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [v1.1.0] - 2026-07-17

基于一次完整实战（单机释放 28.9GB）的安全加固与覆盖扩展。

### 安全加固（重要）
- 🔒 `Package Cache` / `InstallerCache` 从"中优先级可清理"移入**安全红线排除清单**——删除会导致软件无法修复/卸载
- 🔒 浏览器 IndexedDB 从"高优先级(safe)"降级为"低优先级(需确认)"——它是网页应用离线数据而非缓存，误删会掉登录甚至丢数据
- 🔒 排除清单新增红线：系统还原点、`Windows\Installer`、DriverStore、个人数据（Documents/Desktop/Pictures/OneDrive）、微信QQ数据（Tencent Files/xwechat_files）、`.ssh`/`.gnupg`
- 🛡️ 管理员模式明确保留"方案确认"闸门：全自动只免手动跑脚本，不免用户审查

### 新增
- 🆕 `references/knowledge.md` 知识库：红线清单 / Tier 分层惯犯表 / 惯犯定位正则 / 执行守则，形成"模式库快筛 + 知识库逐案研判"两层分析（实测模式库只覆盖约 1/3 可清理空间）
- 🆕 模式库新增：内核崩溃转储（LiveKernelReports/Minidump）、Chrome 端侧AI模型（OptGuideOnDeviceModel，约4GB，附防回归 flag 说明）、$WinREAgent、Playwright 测试浏览器
- 🆕 `skill.md` → `SKILL.md`，补充标准 YAML frontmatter（name/description），符合 Agent Skills 规范可自动触发

### 修复与改进
- 🐛 修复子目录去重误判（`npm-cache2` 被当作 `npm-cache` 的子目录）
- 🐛 analyze.py 兼容 GUI 导出的首行说明行与英文界面列名（File Name/Size）
- 🐛 生成的清理脚本：支持单文件目标；清理时排除 `claude*`（Claude Code 会话自身临时文件）；进程检查扩展到 VS Code / Java(Gradle)；失败时输出原因
- 🔧 scan.py 路径可移植化：不再硬编码绝对路径，相对技能目录定位 + WizTree 自动探测（环境变量 → 技能目录 → Program Files → PATH）
- 🔧 scan.py 默认导出文件行（`--folders-only` 退回旧行为）：单个巨型文件（转储/AI模型/半成品下载）不再隐身，实测这类往往是最大收益
- 🔧 backup.py 优先使用 pwsh（PowerShell 7+），规避 Windows PowerShell 5.1 Compress-Archive 的 4GB 上限

---

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

[v1.1.0]: https://github.com/iziqing/-disk-cleaner/releases/tag/v1.1.0
[v1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
[v0.2.0]: https://github.com/user/repo/releases/tag/v0.2.0
[v0.1.0]: https://github.com/user/repo/releases/tag/v0.1.0
