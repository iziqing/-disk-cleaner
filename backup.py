#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C盘清理备份模块
提供备份、恢复、删除备份等功能，为清理操作提供安全保障
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# 配置
BACKUP_DIR_NAME = "CleanBackups"
SIZE_THRESHOLD = 1 * 1024 * 1024 * 1024  # 1GB - 超过此大小使用压缩


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes >= 1024 ** 3:
        return f"{size_bytes / (1024 ** 3):.2f} GB"
    elif size_bytes >= 1024 ** 2:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes} B"


def get_dir_size(path: str) -> int:
    """获取目录大小"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_dir_size(entry.path)
    except (PermissionError, OSError):
        pass
    return total


def find_backup_drive() -> Optional[str]:
    """
    自动选择非C盘剩余空间最大的驱动器

    Returns:
        str: 备份根目录路径（如 D:\\CleanBackups），空间不足返回 None
    """
    import ctypes

    best_drive = None
    max_free = 0
    min_required = 5 * 1024 * 1024 * 1024  # 最少需要 5GB 可用空间

    # 遍历所有可能的驱动器号
    for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            try:
                # 获取磁盘剩余空间
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(drive), None, None, ctypes.pointer(free_bytes)
                )
                free = free_bytes.value

                if free > max_free and free >= min_required:
                    max_free = free
                    best_drive = letter
            except:
                continue

    if best_drive:
        backup_root = f"{best_drive}:\\{BACKUP_DIR_NAME}"
        return backup_root

    return None


def get_backup_root() -> str:
    """获取备份根目录，不存在则创建"""
    backup_root = find_backup_drive()
    if not backup_root:
        raise RuntimeError("未找到合适的备份驱动器（需要非C盘且至少5GB可用空间）")

    os.makedirs(backup_root, exist_ok=True)
    return backup_root


def sanitize_path_name(path: str) -> str:
    """将路径转换为安全的文件名"""
    # 移除驱动器号和冒号
    name = path.replace(":", "").replace("\\", "_").replace("/", "_")
    # 移除开头的下划线
    name = name.lstrip("_")
    # 限制长度
    if len(name) > 100:
        name = name[:100]
    return name


def create_backup(paths: List[str], priority: str = "high") -> Dict:
    """
    创建备份

    Args:
        paths: 要备份的目录列表
        priority: 优先级标识（high/medium/low）

    Returns:
        dict: 备份信息（包含 manifest）
    """
    backup_root = get_backup_root()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_id = f"backup_{timestamp}"
    backup_dir = os.path.join(backup_root, backup_id)

    os.makedirs(backup_dir, exist_ok=True)

    manifest = {
        "id": backup_id,
        "timestamp": datetime.now().isoformat(),
        "priority": priority,
        "backup_root": backup_root,
        "items": [],
        "status": "in_progress",
        "total_size": 0,
        "total_size_formatted": ""
    }

    print(f"备份目录: {backup_dir}")
    print(f"备份驱动器剩余空间: {format_size(_get_drive_free_space(backup_root))}")
    print("-" * 50)

    for path in paths:
        if not os.path.exists(path):
            print(f"[跳过] 路径不存在: {path}")
            continue

        dir_size = get_dir_size(path)
        if dir_size == 0:
            print(f"[跳过] 目录为空: {path}")
            continue

        safe_name = sanitize_path_name(path)

        # 智能选择备份格式
        if dir_size < SIZE_THRESHOLD:
            # 小于1GB，直接复制
            backup_format = "copy"
            backup_path = os.path.join(backup_dir, safe_name)
            print(f"[备份] {format_size(dir_size):>10} {path}")
            print(f"        → 直接复制到 {backup_path}")

            try:
                # 使用 robocopy 复制（保留属性，支持长路径）
                result = subprocess.run(
                    [
                        "robocopy", path, backup_path,
                        "/E",  # 复制所有子目录
                        "/COPY:DAT",  # 复制数据、属性、时间戳
                        "/R:1",  # 重试1次
                        "/W:1",  # 等待1秒
                        "/NFL", "/NDL", "/NJH", "/NJS",  # 减少输出
                    ],
                    capture_output=True,
                    timeout=300  # 5分钟超时
                )
                # robocopy 返回码 0-3 都表示成功
                if result.returncode > 3:
                    raise RuntimeError(f"robocopy 失败，返回码: {result.returncode}")
                print(f"        [完成]")
            except Exception as e:
                print(f"        [失败] {e}")
                continue
        else:
            # 大于等于1GB，使用压缩
            backup_format = "zip"
            backup_path = os.path.join(backup_dir, f"{safe_name}.zip")
            print(f"[备份] {format_size(dir_size):>10} {path}")
            print(f"        → 压缩到 {backup_path}")

            try:
                # 使用 PowerShell 压缩
                ps_script = f'''
                $ProgressPreference = 'SilentlyContinue'
                Compress-Archive -Path "{path}\\*" -DestinationPath "{backup_path}" -CompressionLevel Optimal -Force
                '''
                result = subprocess.run(
                    ["powershell", "-Command", ps_script],
                    capture_output=True,
                    timeout=1800  # 30分钟超时
                )
                if result.returncode != 0:
                    raise RuntimeError(f"压缩失败: {result.stderr.decode('utf-8', errors='ignore')}")
                print(f"        [完成]")
            except Exception as e:
                print(f"        [失败] {e}")
                continue

        manifest["items"].append({
            "original_path": path,
            "backup_path": backup_path,
            "size": dir_size,
            "size_formatted": format_size(dir_size),
            "format": backup_format
        })
        manifest["total_size"] += dir_size

    manifest["total_size_formatted"] = format_size(manifest["total_size"])
    manifest["status"] = "completed"

    # 保存 manifest
    manifest_path = os.path.join(backup_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("-" * 50)
    print(f"备份完成！共备份 {len(manifest['items'])} 个目录，总计 {manifest['total_size_formatted']}")
    print(f"备份ID: {backup_id}")

    return manifest


def _get_drive_free_space(path: str) -> int:
    """获取驱动器剩余空间"""
    import ctypes
    drive = os.path.splitdrive(path)[0] + "\\"
    free_bytes = ctypes.c_ulonglong(0)
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(
        ctypes.c_wchar_p(drive), None, None, ctypes.pointer(free_bytes)
    )
    return free_bytes.value


def list_backups() -> List[Dict]:
    """
    列出所有备份

    Returns:
        list: 备份信息列表
    """
    backups = []

    try:
        backup_root = get_backup_root()
    except RuntimeError:
        return backups

    if not os.path.exists(backup_root):
        return backups

    for item in os.listdir(backup_root):
        backup_dir = os.path.join(backup_root, item)
        manifest_path = os.path.join(backup_dir, "manifest.json")

        if os.path.isdir(backup_dir) and os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                backups.append(manifest)
            except:
                continue

    # 按时间排序（最新的在前）
    backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return backups


def get_backup(backup_id: str) -> Optional[Dict]:
    """
    获取指定备份的信息

    Args:
        backup_id: 备份ID

    Returns:
        dict: 备份信息，不存在返回 None
    """
    try:
        backup_root = get_backup_root()
    except RuntimeError:
        return None

    backup_dir = os.path.join(backup_root, backup_id)
    manifest_path = os.path.join(backup_dir, "manifest.json")

    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return None


def restore_backup(backup_id: str) -> bool:
    """
    回滚恢复指定备份

    Args:
        backup_id: 备份ID

    Returns:
        bool: 是否成功
    """
    manifest = get_backup(backup_id)
    if not manifest:
        print(f"错误：备份不存在 - {backup_id}")
        return False

    print(f"开始恢复备份: {backup_id}")
    print(f"备份时间: {manifest['timestamp']}")
    print(f"共 {len(manifest['items'])} 个目录")
    print("-" * 50)

    success_count = 0

    for item in manifest["items"]:
        original_path = item["original_path"]
        backup_path = item["backup_path"]
        backup_format = item["format"]

        print(f"[恢复] {original_path}")

        if not os.path.exists(backup_path):
            print(f"        [跳过] 备份文件不存在")
            continue

        try:
            # 确保目标目录存在
            os.makedirs(original_path, exist_ok=True)

            if backup_format == "copy":
                # 直接复制恢复
                result = subprocess.run(
                    [
                        "robocopy", backup_path, original_path,
                        "/E", "/COPY:DAT", "/R:1", "/W:1",
                        "/NFL", "/NDL", "/NJH", "/NJS",
                    ],
                    capture_output=True,
                    timeout=300
                )
                if result.returncode > 3:
                    raise RuntimeError(f"robocopy 失败")
            else:
                # 解压恢复
                ps_script = f'''
                $ProgressPreference = 'SilentlyContinue'
                Expand-Archive -Path "{backup_path}" -DestinationPath "{original_path}" -Force
                '''
                result = subprocess.run(
                    ["powershell", "-Command", ps_script],
                    capture_output=True,
                    timeout=1800
                )
                if result.returncode != 0:
                    raise RuntimeError(f"解压失败")

            print(f"        [完成]")
            success_count += 1
        except Exception as e:
            print(f"        [失败] {e}")

    print("-" * 50)
    print(f"恢复完成！成功 {success_count}/{len(manifest['items'])} 个目录")

    return success_count == len(manifest["items"])


def delete_backup(backup_id: str) -> bool:
    """
    删除指定备份

    Args:
        backup_id: 备份ID

    Returns:
        bool: 是否成功
    """
    try:
        backup_root = get_backup_root()
    except RuntimeError:
        return False

    backup_dir = os.path.join(backup_root, backup_id)

    if not os.path.exists(backup_dir):
        print(f"备份不存在: {backup_id}")
        return False

    try:
        shutil.rmtree(backup_dir)
        print(f"已删除备份: {backup_id}")
        return True
    except Exception as e:
        print(f"删除失败: {e}")
        return False


def cleanup_all_backups() -> int:
    """
    清理所有备份

    Returns:
        int: 删除的备份数量
    """
    backups = list_backups()
    deleted = 0

    for backup in backups:
        if delete_backup(backup["id"]):
            deleted += 1

    return deleted


def get_latest_backup() -> Optional[Dict]:
    """获取最新的备份"""
    backups = list_backups()
    return backups[0] if backups else None


def print_backups_table(backups: List[Dict]):
    """打印备份列表表格"""
    if not backups:
        print("没有找到任何备份")
        return

    print("=" * 70)
    print("                         备份列表")
    print("=" * 70)
    print(f"{'ID':<30} {'时间':<20} {'大小':<12} {'项目数':<8}")
    print("-" * 70)

    for backup in backups:
        backup_id = backup["id"]
        timestamp = backup["timestamp"][:19].replace("T", " ")
        size = backup.get("total_size_formatted", "未知")
        items = len(backup.get("items", []))
        print(f"{backup_id:<30} {timestamp:<20} {size:<12} {items:<8}")

    print("=" * 70)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='C盘清理备份工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # create 命令
    create_parser = subparsers.add_parser('create', help='创建备份')
    create_parser.add_argument('--paths', nargs='+', required=True, help='要备份的目录列表')
    create_parser.add_argument('--priority', default='high', choices=['high', 'medium', 'low'],
                               help='优先级标识')

    # list 命令
    subparsers.add_parser('list', help='列出所有备份')

    # restore 命令
    restore_parser = subparsers.add_parser('restore', help='恢复备份')
    restore_parser.add_argument('--id', required=True, help='备份ID')

    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除备份')
    delete_parser.add_argument('--id', required=True, help='备份ID')

    # cleanup 命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理备份')
    cleanup_parser.add_argument('--all', action='store_true', help='清理所有备份')

    # info 命令
    info_parser = subparsers.add_parser('info', help='显示备份详情')
    info_parser.add_argument('--id', required=True, help='备份ID')

    # drive 命令
    subparsers.add_parser('drive', help='显示备份驱动器信息')

    args = parser.parse_args()

    if args.command == 'create':
        try:
            manifest = create_backup(args.paths, args.priority)
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
        except RuntimeError as e:
            print(f"错误: {e}")
            sys.exit(1)

    elif args.command == 'list':
        backups = list_backups()
        print_backups_table(backups)

    elif args.command == 'restore':
        success = restore_backup(args.id)
        sys.exit(0 if success else 1)

    elif args.command == 'delete':
        success = delete_backup(args.id)
        sys.exit(0 if success else 1)

    elif args.command == 'cleanup':
        if args.all:
            deleted = cleanup_all_backups()
            print(f"已清理 {deleted} 个备份")
        else:
            print("请指定 --all 参数以确认清理所有备份")

    elif args.command == 'info':
        manifest = get_backup(args.id)
        if manifest:
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
        else:
            print(f"备份不存在: {args.id}")
            sys.exit(1)

    elif args.command == 'drive':
        backup_root = find_backup_drive()
        if backup_root:
            free_space = _get_drive_free_space(backup_root)
            print(f"备份驱动器: {backup_root}")
            print(f"剩余空间: {format_size(free_space)}")
        else:
            print("未找到合适的备份驱动器（需要非C盘且至少5GB可用空间）")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
