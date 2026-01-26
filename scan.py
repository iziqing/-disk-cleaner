#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WizTree 自动扫描脚本
自动调用 WizTree 扫描并等待导出完成
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

# 配置
WIZTREE_PATH = r"F:\coding\xianliao\WizTree\WizTree64.exe"
DATA_DIR = r"F:\coding\xianliao\skills\clean-c-drive\data"


def check_admin():
    """检查是否有管理员权限"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def wait_for_file(filepath, timeout=120, stable_time=2):
    """
    等待文件生成并稳定

    Args:
        filepath: 文件路径
        timeout: 超时时间（秒）
        stable_time: 文件大小稳定时间（秒）

    Returns:
        bool: 文件是否准备好
    """
    print(f"等待扫描完成...")
    start = time.time()
    last_size = -1
    stable_count = 0

    while time.time() - start < timeout:
        if os.path.exists(filepath):
            try:
                size = os.path.getsize(filepath)
                if size > 0:
                    if size == last_size:
                        stable_count += 1
                        if stable_count >= stable_time:
                            # 文件大小稳定，扫描完成
                            print(f"扫描完成！文件大小: {size / 1024 / 1024:.2f} MB")
                            return True
                    else:
                        stable_count = 0
                    last_size = size

                    # 显示进度
                    elapsed = int(time.time() - start)
                    print(f"\r扫描中... {elapsed}s, 当前文件大小: {size / 1024 / 1024:.2f} MB", end="", flush=True)
            except:
                pass

        time.sleep(1)

    print(f"\n超时！等待了 {timeout} 秒")
    return False


def scan(drive="C:", top_folders=300, include_files=False):
    """
    执行 WizTree 扫描

    Args:
        drive: 要扫描的驱动器
        top_folders: 导出的文件夹数量
        include_files: 是否包含文件（False 只导出文件夹）

    Returns:
        str: 导出的 CSV 文件路径，失败返回 None
    """
    # 检查管理员权限
    if not check_admin():
        print("错误：需要管理员权限才能扫描")
        print("请以管理员身份运行此脚本")
        return None

    # 检查 WizTree 是否存在
    if not os.path.exists(WIZTREE_PATH):
        print(f"错误：找不到 WizTree: {WIZTREE_PATH}")
        return None

    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(DATA_DIR, f"scan_{timestamp}.csv")

    # 构建命令
    # /admin=1 - 管理员模式
    # /exportfolders=1 - 导出文件夹
    # /exportfiles=0/1 - 是否导出文件
    # /sortby=2 - 按大小排序
    # /exportdrivecapacity=1 - 包含驱动器容量信息
    # /exportmaxdepth=200 - 最大文件夹深度（减小文件大小，加快分析）
    cmd = [
        WIZTREE_PATH,
        drive,
        f'/export={output_file}',
        '/admin=1',
        '/exportfolders=1',
        f'/exportfiles={1 if include_files else 0}',
        '/sortby=2',
        '/exportdrivecapacity=1',
        '/exportmaxdepth=200',
    ]

    print(f"开始扫描 {drive}")
    print(f"输出文件: {output_file}")
    print(f"命令: {' '.join(cmd)}")
    print("-" * 50)

    try:
        # 启动 WizTree（非阻塞）
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )

        # 等待文件生成并稳定
        if wait_for_file(output_file, timeout=120):
            # 等待进程结束
            process.wait(timeout=10)
            print(f"\n扫描成功！")
            print(f"数据文件: {output_file}")

            # 清理旧数据，只保留最新一份
            deleted = cleanup_old_scans(keep_latest=1)
            if deleted > 0:
                print(f"已清理 {deleted} 个旧数据文件")

            return output_file
        else:
            # 超时，终止进程
            process.terminate()
            print("扫描超时或失败")
            return None

    except subprocess.TimeoutExpired:
        process.terminate()
        print("进程超时")
        return None
    except Exception as e:
        print(f"扫描出错: {e}")
        return None


def get_latest_scan():
    """获取最新的扫描文件"""
    data_path = Path(DATA_DIR)
    if not data_path.exists():
        return None

    csv_files = list(data_path.glob("*.csv"))
    if not csv_files:
        return None

    # 按修改时间排序，返回最新的
    latest = max(csv_files, key=lambda f: f.stat().st_mtime)
    return str(latest)


def cleanup_old_scans(keep_latest=1):
    """
    清理旧的扫描文件，只保留最新的几份

    Args:
        keep_latest: 保留最新的几份文件（默认 1）

    Returns:
        int: 删除的文件数量
    """
    data_path = Path(DATA_DIR)
    deleted = 0

    # 清理 CSV 数据文件
    if data_path.exists():
        csv_files = list(data_path.glob("*.csv"))
        if len(csv_files) > keep_latest:
            # 按修改时间排序（最新的在前）
            csv_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            # 删除旧文件
            for old_file in csv_files[keep_latest:]:
                try:
                    old_file.unlink()
                    print(f"已删除旧数据: {old_file.name}")
                    deleted += 1
                except Exception as e:
                    print(f"删除失败 {old_file.name}: {e}")

    # 清理生成的清理脚本 (clean_*.ps1)
    skill_path = Path(DATA_DIR).parent
    clean_scripts = list(skill_path.glob("clean_*.ps1"))
    for script in clean_scripts:
        try:
            script.unlink()
            print(f"已删除清理脚本: {script.name}")
            deleted += 1
        except Exception as e:
            print(f"删除失败 {script.name}: {e}")

    return deleted


def main():
    import argparse

    parser = argparse.ArgumentParser(description='WizTree 自动扫描工具')
    parser.add_argument('drive', nargs='?', default='C:', help='要扫描的驱动器 (默认: C:)')
    parser.add_argument('--include-files', action='store_true', help='包含文件（默认只扫描文件夹）')
    parser.add_argument('--timeout', type=int, default=120, help='扫描超时时间（秒）')
    parser.add_argument('--latest', action='store_true', help='显示最新的扫描文件')
    parser.add_argument('--cleanup', action='store_true', help='清理旧数据，只保留最新一份')

    args = parser.parse_args()

    if args.cleanup:
        deleted = cleanup_old_scans(keep_latest=1)
        if deleted > 0:
            print(f"已清理 {deleted} 个旧数据文件")
        else:
            print("没有需要清理的旧数据")
        return

    if args.latest:
        latest = get_latest_scan()
        if latest:
            print(f"最新扫描文件: {latest}")
        else:
            print("没有找到扫描文件")
        return

    # 执行扫描
    result = scan(
        drive=args.drive,
        include_files=args.include_files
    )

    if result:
        print(f"\n可以使用以下命令分析:")
        print(f'python analyze.py "{result}" --min-size 50')
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
