# WizTree C盘扫描脚本
# 需要以管理员权限运行
# 用法: 右键 -> 以管理员身份运行

param(
    [string]$WizTreePath = "F:\coding\xianliao\WizTree\WizTree64.exe",
    [string]$OutputDir = "F:\coding\xianliao\skills\clean-c-drive\data",
    [string]$Drive = "C:"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    WizTree C盘扫描工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[错误] 请以管理员权限运行此脚本!" -ForegroundColor Red
    Write-Host "右键点击此脚本 -> 以管理员身份运行" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

# 检查 WizTree 是否存在
if (-not (Test-Path $WizTreePath)) {
    Write-Host "[错误] 找不到 WizTree: $WizTreePath" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 创建输出目录
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# 生成输出文件名
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = Join-Path $OutputDir "scan_$timestamp.csv"

Write-Host "WizTree 路径: $WizTreePath" -ForegroundColor Gray
Write-Host "扫描目标: $Drive" -ForegroundColor Gray
Write-Host "输出文件: $outputFile" -ForegroundColor Gray
Write-Host ""

Write-Host "正在扫描 $Drive ..." -ForegroundColor Yellow
Write-Host "(这可能需要几秒钟)" -ForegroundColor Gray
Write-Host ""

# 运行 WizTree 扫描
try {
    # 使用 start /wait 确保等待扫描完成
    # 参数说明:
    # /admin=1 - 使用管理员模式进行 MFT 扫描
    # /export - 导出到 CSV 文件
    # /exportfolders=1 - 导出文件夹
    # /exportfiles=0 - 不导出文件（减小文件大小）
    # /exportdrivecapacity=1 - 导出磁盘容量信息

    $arguments = "`"$Drive`" /export=`"$outputFile`" /admin=1 /exportfolders=1 /exportfiles=0 /exportdrivecapacity=1"

    Write-Host "执行命令: $WizTreePath $arguments" -ForegroundColor Gray

    $process = Start-Process -FilePath $WizTreePath -ArgumentList $arguments -Wait -PassThru

    # 等待文件生成（WizTree 可能需要一点时间）
    Start-Sleep -Seconds 2
}
catch {
    Write-Host "[错误] 扫描失败: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查输出文件
if (-not (Test-Path $outputFile)) {
    Write-Host "[错误] 扫描完成但未生成输出文件" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

$fileSize = (Get-Item $outputFile).Length / 1MB
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "扫描完成!" -ForegroundColor Green
Write-Host "输出文件: $outputFile" -ForegroundColor White
Write-Host "文件大小: $([math]::Round($fileSize, 2)) MB" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "现在可以使用 /clean-c-drive 命令让 AI 分析扫描结果" -ForegroundColor Yellow

Read-Host "按回车键退出"
