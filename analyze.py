#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WizTree CSV 分析工具
分析扫描结果，识别可清理的目录
"""

import csv
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 可清理目录的模式定义
CLEANABLE_PATTERNS = {
    "high": {
        "name": "高优先级（安全清理）",
        "patterns": [
            {"pattern": "softwaredistr", "name": "Windows 更新缓存", "safe": True},
            {"pattern": "ota-artifacts", "name": "NVIDIA 更新缓存", "safe": True},
            {"pattern": "indexeddb", "name": "浏览器 IndexedDB 缓存", "safe": True},
            {"pattern": "\\pip\\cache", "name": "pip 缓存", "safe": True},
            {"pattern": "\\.cache\\puppeteer", "name": "puppeteer 缓存", "safe": True},
            {"pattern": "\\electron\\cache", "name": "electron 缓存", "safe": True},
            {"pattern": "\\bcut\\cache", "name": "BCUT 缓存", "safe": True},
            {"pattern": "\\npm-cache", "name": "npm 缓存", "safe": True},
            {"pattern": "\\yarn\\cache", "name": "yarn 缓存", "safe": True},
            {"pattern": "\\temp\\", "name": "临时文件", "safe": True},
            {"pattern": "\\tmp\\", "name": "临时文件", "safe": True},
        ]
    },
    "medium": {
        "name": "中优先级（谨慎清理）",
        "patterns": [
            {"pattern": "\\cache\\", "name": "应用缓存", "safe": False},
            {"pattern": "\\caches\\", "name": "应用缓存", "safe": False},
            {"pattern": "\\logs\\", "name": "日志文件", "safe": False},
            {"pattern": "crashdump", "name": "崩溃转储", "safe": False},
            {"pattern": "\\package cache", "name": "安装包缓存", "safe": False},
            {"pattern": "installercache", "name": "安装包缓存", "safe": False},
            {"pattern": "gpucache", "name": "GPU 缓存", "safe": False},
            {"pattern": "shadercache", "name": "着色器缓存", "safe": False},
            {"pattern": "code cache", "name": "代码缓存", "safe": False},
            {"pattern": "service worker", "name": "Service Worker 缓存", "safe": False},
        ]
    },
    "low": {
        "name": "低优先级（需确认）",
        "patterns": [
            {"pattern": "\\.gradle\\caches", "name": "Gradle 缓存", "safe": False},
            {"pattern": "\\.cargo\\registry", "name": "Cargo 缓存", "safe": False},
            {"pattern": "\\.nuget\\packages", "name": "NuGet 缓存", "safe": False},
            {"pattern": "\\go\\pkg\\mod", "name": "Go Modules 缓存", "safe": False},
        ]
    }
}

# 需要排除的系统目录
EXCLUDE_PATTERNS = [
    "\\windows\\winsxs",
    "\\windows\\system32",
    "\\windows\\syswow64",
    "\\program files\\",
    "\\program files (x86)\\",
    "\\programdata\\microsoft\\windows\\",
]


def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes >= 1024 ** 3:
        return f"{size_bytes / (1024 ** 3):.2f} GB"
    elif size_bytes >= 1024 ** 2:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes} B"


def analyze_csv(csv_path, min_size_mb=50):
    """分析 CSV 文件"""
    results = {
        "scan_file": csv_path,
        "scan_time": datetime.now().isoformat(),
        "total_size": 0,
        "free_space": 0,
        "used_space": 0,
        "categories": {
            "high": {"name": "高优先级（安全清理）", "items": [], "total_size": 0},
            "medium": {"name": "中优先级（谨慎清理）", "items": [], "total_size": 0},
            "low": {"name": "低优先级（需确认）", "items": [], "total_size": 0},
        }
    }

    min_size = min_size_mb * 1024 * 1024

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                path = row.get('文件名称', '')
                size = int(row.get('大小', 0))

                # 获取驱动器信息（只有根目录有）
                if path == "C:\\" or path == "C:":
                    results["total_size"] = int(row.get('DRIVECAPACITY', 0))
                    results["free_space"] = int(row.get('FREESPACE', 0))
                    results["used_space"] = int(row.get('USEDSPACE', 0))

                # 跳过小文件和排除目录
                if size < min_size:
                    continue

                path_lower = path.lower()

                # 检查是否在排除列表中
                is_excluded = any(exc in path_lower for exc in EXCLUDE_PATTERNS)
                if is_excluded:
                    continue

                # 检查匹配的清理类别
                for priority, category in CLEANABLE_PATTERNS.items():
                    for pattern_info in category["patterns"]:
                        if pattern_info["pattern"] in path_lower:
                            # 检查是否已经有父目录在列表中
                            existing_paths = [item["path"] for item in results["categories"][priority]["items"]]
                            is_subdir = any(path.startswith(p) and path != p for p in existing_paths)

                            if not is_subdir:
                                # 移除已有的子目录
                                results["categories"][priority]["items"] = [
                                    item for item in results["categories"][priority]["items"]
                                    if not item["path"].startswith(path)
                                ]

                                results["categories"][priority]["items"].append({
                                    "path": path,
                                    "size": size,
                                    "size_formatted": format_size(size),
                                    "name": pattern_info["name"],
                                    "safe": pattern_info["safe"]
                                })
                            break
                    else:
                        continue
                    break
            except (ValueError, KeyError):
                continue

    # 计算每个类别的总大小并排序
    for priority in results["categories"]:
        items = results["categories"][priority]["items"]
        items.sort(key=lambda x: x["size"], reverse=True)
        results["categories"][priority]["total_size"] = sum(item["size"] for item in items)
        results["categories"][priority]["total_size_formatted"] = format_size(
            results["categories"][priority]["total_size"]
        )

    return results


def print_report(results):
    """打印分析报告"""
    print("=" * 60)
    print("           C盘清理分析报告")
    print("=" * 60)
    print()

    if results["total_size"] > 0:
        print(f"磁盘总容量: {format_size(results['total_size'])}")
        print(f"已用空间:   {format_size(results['used_space'])}")
        print(f"可用空间:   {format_size(results['free_space'])}")
        print()

    total_cleanable = 0

    for priority in ["high", "medium", "low"]:
        category = results["categories"][priority]
        if category["items"]:
            print("-" * 60)
            print(f"【{category['name']}】 - 共 {category['total_size_formatted']}")
            print("-" * 60)

            for item in category["items"][:10]:  # 只显示前10个
                print(f"  {item['size_formatted']:>10}  {item['name']}")
                print(f"             {item['path']}")

            if len(category["items"]) > 10:
                print(f"  ... 还有 {len(category['items']) - 10} 个目录")

            print()
            total_cleanable += category["total_size"]

    print("=" * 60)
    print(f"潜在可清理空间: {format_size(total_cleanable)}")
    print("=" * 60)


def generate_clean_script(results, output_path, priority="high"):
    """生成清理脚本"""
    items = results["categories"][priority]["items"]

    script = '''# C盘清理脚本 - {priority_name}
# 自动生成于: {timestamp}
# 需要以管理员权限运行

param(
    [switch]$Force
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       C盘清理工具 - {priority_name}" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {{
    Write-Host "[警告] 未以管理员权限运行，部分目录可能无法清理" -ForegroundColor Yellow
}}

# 检查浏览器
$chrome = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
$edge = Get-Process -Name "msedge" -ErrorAction SilentlyContinue
if ($chrome -or $edge) {{
    Write-Host "[警告] 浏览器正在运行，部分缓存可能无法清理" -ForegroundColor Yellow
}}

$cleanTargets = @(
{targets}
)

Write-Host "将要清理以下目录:" -ForegroundColor White
foreach ($target in $cleanTargets) {{
    $exists = Test-Path $target.Path
    $status = if ($exists) {{ "[存在]" }} else {{ "[不存在]" }}
    $color = if ($exists) {{ "Green" }} else {{ "Gray" }}
    Write-Host "  $status $($target.Name) - $($target.Size)" -ForegroundColor $color
}}

if (-not $Force) {{
    $confirm = Read-Host "`n确认清理? (Y/N)"
    if ($confirm -ne "Y" -and $confirm -ne "y") {{
        Write-Host "已取消" -ForegroundColor Yellow
        exit
    }}
}}

Write-Host "`n开始清理..." -ForegroundColor Cyan

$totalCleaned = 0
foreach ($target in $cleanTargets) {{
    Write-Host "清理: $($target.Name)..." -NoNewline
    if (-not (Test-Path $target.Path)) {{
        Write-Host " [跳过]" -ForegroundColor Gray
        continue
    }}
    try {{
        $before = (Get-ChildItem -Path $target.Path -Recurse -Force -EA SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        Remove-Item -Path "$($target.Path)\\*" -Recurse -Force -EA Stop
        $cleanedMB = [math]::Round($before / 1MB, 2)
        $totalCleaned += $cleanedMB
        Write-Host " [完成 - $cleanedMB MB]" -ForegroundColor Green
    }} catch {{
        Write-Host " [失败]" -ForegroundColor Red
    }}
}}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "清理完成! 总计: $([math]::Round($totalCleaned / 1024, 2)) GB" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
'''

    # 生成目标列表
    targets_str = ""
    for item in items:
        path = item["path"].replace("\\", "\\\\").replace("'", "''")
        targets_str += f'''    @{{
        Name = "{item['name']}"
        Path = "{path}"
        Size = "{item['size_formatted']}"
    }},
'''

    script = script.format(
        priority_name=results["categories"][priority]["name"],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        targets=targets_str.rstrip(",\n")
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(script)

    return output_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description='WizTree CSV 分析工具')
    parser.add_argument('csv_file', help='WizTree 导出的 CSV 文件路径')
    parser.add_argument('--min-size', type=int, default=50, help='最小文件大小 (MB)')
    parser.add_argument('--output', help='输出清理脚本路径')
    parser.add_argument('--priority', choices=['high', 'medium', 'low', 'all'], default='high',
                        help='生成清理脚本的优先级')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')

    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        print(f"错误: 文件不存在 - {args.csv_file}")
        sys.exit(1)

    results = analyze_csv(args.csv_file, args.min_size)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_report(results)

    if args.output:
        generate_clean_script(results, args.output, args.priority)
        print(f"\n清理脚本已生成: {args.output}")


if __name__ == "__main__":
    main()
