# /clean-c-drive Skill

利用 WizTree 的快速扫描能力和 AI 的智能分析能力，清理 C 盘垃圾文件。

## 工作流程

### 阶段 1: 检查权限和扫描数据

1. **检查管理员权限**：
   ```bash
   powershell -Command "([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)"
   ```

2. **如果有管理员权限（返回 True）**：
   - 检查 `data/` 目录是否有最近的扫描文件
   - 如果没有或超过 24 小时，自动调用 scan.py 扫描：
     ```bash
     python "F:\coding\xianliao\skills\clean-c-drive\scan.py" C:
     ```
   - 等待扫描完成，自动获取数据

3. **如果没有管理员权限（返回 False）**：
   - 检查 `data/` 目录是否有扫描文件
   - 如果有，使用现有数据
   - 如果没有，提示用户：
     ```
     当前没有管理员权限，无法自动扫描。

     请选择：
     1. 以管理员权限重新启动 Claude Code（推荐，可全自动）
     2. 手动运行 WizTree 导出数据到 data 目录，然后再次运行此命令
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

**如果有管理员权限：**
- 直接使用 PowerShell 删除选中的目录
- 显示清理进度和结果

**如果没有管理员权限：**
1. 生成清理脚本到 `F:\coding\xianliao\skills\clean-c-drive\clean_<level>.ps1`
2. 提示用户以管理员权限运行脚本
3. 显示清理结果

### 阶段 5: 清理临时文件

清理任务完成后，询问用户是否删除临时文件：
```
清理已完成！是否删除扫描数据和清理脚本？
- 删除（推荐，保持目录整洁）
- 保留
```

如果用户选择删除，执行：
```bash
python "F:\coding\xianliao\skills\clean-c-drive\scan.py" --cleanup
```

将清理以下文件：
- `data/*.csv` - 扫描数据文件
- `clean_*.ps1` - 生成的清理脚本

## 核心脚本

### scan.py - 自动扫描

功能：
- 检查管理员权限
- 调用 WizTree 命令行扫描
- 等待文件生成并稳定
- 返回扫描结果路径

用法：
```bash
# 扫描 C 盘
python scan.py C:

# 查看最新扫描文件
python scan.py --latest
```

### analyze.py - 数据分析

功能：
- 解析 WizTree CSV 文件
- 按优先级分类可清理目录
- 生成 JSON 格式报告
- 生成清理脚本

用法：
```bash
# 分析并显示报告
python analyze.py "data/scan_xxx.csv" --min-size 50

# 输出 JSON 格式
python analyze.py "data/scan_xxx.csv" --json

# 生成清理脚本
python analyze.py "data/scan_xxx.csv" --output "clean.ps1" --priority high
```

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
- 安装包缓存: `Package Cache`

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
├── skill.md          # Skill 定义（本文件）
├── scan.py           # 自动扫描脚本（Python）
├── analyze.py        # 分析脚本
├── README.md         # 项目说明
├── GUIDE.md          # 操作指南
├── data/             # 扫描数据目录（临时）
│   └── *.csv         # WizTree 导出的扫描结果
├── clean_*.ps1       # AI 临时生成的清理脚本（执行后删除）
└── docs/             # 文档
    └── rust-disk-scanner-spec.md  # Rust 扫描工具规划
```

**注意：** `clean_*.ps1` 清理脚本由 AI 根据实际扫描结果临时生成，执行完成后会被清理删除。

## WizTree 命令行参考

```bash
WizTree64.exe <drive> /export="<path>" [options]

选项：
  /admin=1              以管理员模式运行
  /exportfolders=1      导出文件夹
  /exportfiles=0        不导出文件（只要文件夹）
  /sortby=2             按大小排序
  /exportdrivecapacity=1 包含驱动器容量信息
  /exportmaxdepth=200   最大文件夹深度（减小文件大小，加快分析）
```

**注意：** 设置 `/exportmaxdepth=200` 可以将导出文件从 160MB 减小到 10-20MB，大幅加快分析速度。

## 使用示例

### 全自动模式（管理员）
```
1. 以管理员身份启动 Claude Code
2. 输入 /clean-c-drive
3. AI 自动扫描 → 分析 → 询问 → 清理
```

### 手动模式（无管理员权限）
```
1. 手动运行 WizTree，导出 CSV 到 data 目录
2. 输入 /clean-c-drive
3. AI 分析现有数据 → 询问 → 生成清理脚本
4. 用户以管理员身份运行清理脚本
```
