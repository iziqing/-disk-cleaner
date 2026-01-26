# /clean-c-drive Skill

利用 WizTree 的快速扫描能力和 AI 的智能分析能力，清理 C 盘垃圾文件。

## 工作流程

### 阶段 1: 检查扫描数据

1. 检查 `F:\coding\xianliao\skills\clean-c-drive\data\` 目录下是否有最近的扫描文件 (scan_*.csv)
2. 如果没有扫描文件，或文件超过 24 小时，提示用户运行扫描脚本：
   ```
   请以管理员身份运行扫描脚本：
   F:\coding\xianliao\skills\clean-c-drive\scan.ps1
   ```

### 阶段 2: 分析扫描数据

使用 Python 分析脚本读取 CSV 文件：

```bash
python "F:\coding\xianliao\skills\clean-c-drive\analyze.py" "<csv_file>" --min-size 50
```

分析内容：
- 识别可清理的目录（按优先级分类）
- 计算潜在可释放空间
- 生成清理报告

### 阶段 3: 生成清理方案

根据分析结果，向用户展示：

1. **磁盘概况**：总容量、已用、可用空间
2. **可清理目录**（按优先级）：
   - 🔴 高优先级（安全清理）：临时文件、浏览器缓存、更新缓存等
   - 🟡 中优先级（谨慎清理）：应用缓存、日志文件等
   - 🟢 低优先级（需确认）：开发工具缓存等

3. **询问用户**：选择清理级别（高/中/低/全部）

### 阶段 4: 执行清理

1. 生成清理脚本到 `F:\coding\xianliao\skills\clean-c-drive\clean_<timestamp>.ps1`
2. 提示用户以管理员权限运行脚本
3. 显示清理结果

## 可清理目录定义

### 高优先级（安全清理）
- Windows 更新缓存: `SoftwareDistribution\Download`
- NVIDIA 更新缓存: `ota-artifacts`
- 浏览器 IndexedDB: `IndexedDB`
- pip 缓存: `pip\cache`
- npm 缓存: `npm-cache`
- yarn 缓存: `yarn\cache`
- puppeteer 缓存: `.cache\puppeteer`
- electron 缓存: `electron\Cache`
- 临时文件: `\Temp\`, `\tmp\`

### 中优先级（谨慎清理）
- 应用缓存: `\Cache\`, `\Caches\`
- 日志文件: `\Logs\`
- 崩溃转储: `CrashDumps`
- GPU 缓存: `GPUCache`, `ShaderCache`
- Service Worker: `Service Worker`

### 低优先级（需确认）
- Gradle 缓存: `.gradle\caches`
- Cargo 缓存: `.cargo\registry`
- Go Modules: `go\pkg\mod`
- NuGet 缓存: `.nuget\packages`

## 安全规则

1. **永远不要删除**：
   - Windows 系统文件 (`\Windows\System32`, `\Windows\WinSxS`)
   - Program Files 目录
   - 用户文档和数据

2. **清理前检查**：
   - 浏览器是否运行（影响浏览器缓存清理）
   - 是否有管理员权限

3. **用户确认**：
   - 显示将要删除的目录列表
   - 等待用户确认后再执行

## 文件结构

```
F:\coding\xianliao\skills\clean-c-drive\
├── scan.ps1          # 扫描脚本（管理员运行）
├── analyze.py        # 分析脚本
├── skill.md          # Skill 定义（本文件）
├── data/             # 扫描数据目录
│   └── scan_*.csv    # 扫描结果
└── clean_*.ps1       # 生成的清理脚本
```

## 使用示例

用户: `/clean-c-drive`

AI 响应:
1. 检查扫描数据
2. 分析并展示清理报告
3. 询问清理级别
4. 生成并提供清理脚本
