# Claude 磁盘清理器

🧹 **人机协作磁盘清理工具**

利用 **WizTree 快速扫描** + **AI 智能分析**，高效清理磁盘空间。

[English Documentation](./docs/README_EN.md)

## 特性

- ⚡ **极速扫描**：使用 WizTree 的 MFT 扫描技术，秒级完成
- 🤖 **AI 分析**：智能识别可清理目录，按优先级分类
- 🎯 **优先级分类**：高/中/低三级清理建议
- 🔒 **安全清理**：永不删除系统文件和用户数据
- 🤝 **人机协作**：两种模式满足不同用户需求

## 两种模式

### 模式一：普通权限 CLI

```
👤 人类：扫描 + 导出数据
🤖 AI：分析 + 生成清理脚本
👤 人类：执行清理脚本
```

适合：注重安全的用户

### 模式二：管理员权限 CLI（推荐）

```
👤 人类：只需说"帮我清理C盘"
🤖 AI：自动扫描 + 分析 + 执行清理
```

适合：追求效率的用户

## 快速开始

### 前置要求

- [WizTree](https://diskanalyzer.com/) - 免费磁盘空间分析器
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) - Anthropic 的 CLI 工具
- Python 3.x

### 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/iziqing/-disk-cleaner.git
   cd -disk-cleaner
   ```

2. 将 WizTree 放入 `WizTree/` 目录（或修改配置中的路径）

3. 复制命令到你的项目：
   ```bash
   cp -r .claude/commands/clean-c-drive.md 你的项目/.claude/commands/
   cp -r skills/clean-c-drive 你的项目/skills/
   ```

### 使用方法

**管理员权限模式（推荐）：**

```powershell
# 以管理员身份打开终端
claude

# 输入命令：
/clean-c-drive
```

**普通权限模式：**

1. 以管理员身份运行 WizTree，扫描并导出 CSV
2. 保存到 `skills/clean-c-drive/data/`
3. 在 Claude Code 中运行 `/clean-c-drive`

## 清理内容

### 高优先级（安全清理）
| 类别 | 说明 |
|------|------|
| Windows 更新缓存 | `SoftwareDistribution\Download` |
| NVIDIA 更新缓存 | `ota-artifacts` |
| 浏览器 IndexedDB | 视频网站缓存 |
| pip/npm/yarn 缓存 | 包管理器缓存 |
| 临时文件 | Temp 目录 |

### 中优先级（谨慎清理）
| 类别 | 说明 |
|------|------|
| 应用缓存 | 各种应用程序缓存 |
| 日志文件 | 应用程序日志 |
| GPU 缓存 | 着色器缓存 |

### 低优先级（需确认）
| 类别 | 说明 |
|------|------|
| Gradle 缓存 | 构建缓存 |
| Cargo 缓存 | Rust 包缓存 |
| Go Modules | Go 包缓存 |

## 工作原理

```
┌─────────────────────────────────────────────────────────────┐
│                      工作流程                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  WizTree    │───▶│  AI Agent   │───▶│   执行清理   │     │
│  │  快速扫描    │    │  智能分析    │    │             │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│        │                  │                  │              │
│        ▼                  ▼                  ▼              │
│   MFT 扫描          智能模式识别         安全删除           │
│   (秒级完成)         优先级分类          确认后执行          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 配置

### 自定义清理规则

编辑 `skills/clean-c-drive/analyze.py`：

```python
CLEANABLE_PATTERNS = {
    "high": {
        "patterns": [
            {"pattern": "你的模式", "name": "描述", "safe": True},
        ]
    }
}
```

### WizTree 路径

修改 `skills/clean-c-drive/scan.ps1`：

```powershell
param(
    [string]$WizTreePath = "你的路径\WizTree64.exe",
    ...
)
```

## 贡献

欢迎提交 Pull Request！

## 许可证

MIT License - 详见 [LICENSE](./LICENSE)

## 致谢

- [WizTree](https://diskanalyzer.com/) - 世界上最快的磁盘空间分析器
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) - AI 驱动的 CLI 工具

## 免责声明

⚠️ **使用风险自负。** 请在确认删除前仔细查看清理报告。作者不对任何数据丢失负责。
