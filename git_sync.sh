# 需要同步时，复制到bash窗口运行：bash /d/22_CodeProjects/yeast-GEM_GuiY/git_sync.sh

'''
project_path="/d/22_CodeProjects/yeast-GEM_GuiY"
project_path="/e/22_CodeProjects/yeast-GEM_GuiY"
'''

#!/bin/bash

# 多电脑Git同步脚本（带自动冲突解决）

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的文本
print_colored() {
    local color=$1
    local text=$2
    case $color in
        red)    echo -e "${RED}${text}${NC}" ;;
        green)  echo -e "${GREEN}${text}${NC}" ;;
        yellow) echo -e "${YELLOW}${text}${NC}" ;;
        blue)   echo -e "${BLUE}${text}${NC}" ;;
        magenta) echo -e "${MAGENTA}${text}${NC}" ;;
        cyan)   echo -e "${CYAN}${text}${NC}" ;;
        *)      echo -e "${text}" ;;
    esac
}

# 运行Git命令并处理错误
run_git_command() {
    if ! git_output=$(git "$@" 2>&1); then
        print_colored red "错误: $git_output"
        return 1
    fi
    echo "$git_output"
    return 0
}

# 获取当前分支名
get_current_branch() {
    git branch --show-current
}

# 自动解决冲突
resolve_conflicts() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_dir="conflict_backup_$timestamp"
    
    print_colored yellow "检测到合并冲突，正在尝试自动解决..."
    
    # 创建备份目录
    mkdir -p "$backup_dir" || {
        print_colored red "无法创建备份目录"
        return 1
    }
    
    # 获取冲突文件列表
    local conflict_files=$(git diff --name-only --diff-filter=U)
    
    if [ -z "$conflict_files" ]; then
        print_colored yellow "没有找到冲突文件"
        return 0
    fi
    
    print_colored yellow "发现以下冲突文件:"
    echo "$conflict_files"
    
    # 备份冲突文件并使用远程版本解决
    for file in $conflict_files; do
        if [ -f "$file" ]; then
            # 创建子目录结构
            local file_dir=$(dirname "$file")
            mkdir -p "$backup_dir/$file_dir"
            
            # 备份文件
            cp "$file" "$backup_dir/$file" && \
            print_colored cyan "已备份冲突文件: $file -> $backup_dir/$file"
            
            # 使用远程版本解决冲突
            git checkout --theirs "$file"
            git add "$file"
        fi
    done
    
    # 提交合并结果
    local commit_msg="自动合并冲突于 $timestamp (备份在 $backup_dir)"
    if ! run_git_command commit -m "$commit_msg"; then
        print_colored red "自动提交合并结果失败"
        return 1
    fi
    
    print_colored green "冲突已自动解决，备份在 $backup_dir"
    return 0
}

# 开始开发前的同步操作
sync_before_start() {
    print_colored cyan "\n$(printf '=%.0s' {1..50})"
    print_colored cyan "在 $(date '+%Y-%m-%d %H:%M:%S') 开始同步"
    print_colored cyan "仓库路径: $(pwd)"
    print_colored cyan "$(printf '=%.0s' {1..50})\n"
    
    # 获取当前分支
    local current_branch=$(get_current_branch)
    if [ -z "$current_branch" ]; then
        print_colored red "无法确定当前分支"
        return 1
    fi
    
    print_colored blue "当前分支: $current_branch"
    
    # 检查是否有未提交的更改
    local status=$(git status --porcelain)
    if [ -n "$status" ]; then
        print_colored yellow "警告: 有未提交的更改存在:"
        echo "$status"
        read -p "是否要暂存并提交这些更改? (y/n): " choice
        if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
            read -p "输入提交信息 (留空使用默认信息): " commit_message
            if [ -z "$commit_message" ]; then
                commit_message="自动提交于 $(date '+%Y-%m-%d %H:%M:%S')"
            fi
            run_git_command add . || return 1
            run_git_command commit -m "$commit_message" || return 1
        else
            print_colored yellow "继续操作可能会丢失未提交的更改!"
            return 1
        fi
    fi
    
    # 获取远程最新更改
    print_colored blue "\n正在获取远程更新..."
    run_git_command fetch || return 1
    
    # 检查是否需要合并
    local behind=$(git rev-list HEAD..origin/$current_branch --count)
    if [ "$behind" -gt 0 ]; then
        print_colored blue "有 $behind 个新提交需要合并"
        
        # 尝试合并
        if ! run_git_command merge origin/$current_branch; then
            if [[ "$git_output" == *"CONFLICT"* ]]; then
                resolve_conflicts || return 1
            else
                print_colored red "合并失败"
                return 1
            fi
        else
            print_colored green "合并成功"
        fi
    else
        print_colored green "已经是最新版本，无需合并"
    fi
    
    print_colored green "\n同步完成，可以开始开发!"
    return 0
}

# 开发结束后的同步操作
sync_after_finish() {
    print_colored magenta "\n$(printf '=%.0s' {1..50})"
    print_colored magenta "在 $(date '+%Y-%m-%d %H:%M:%S') 结束同步"
    print_colored magenta "仓库路径: $(pwd)"
    print_colored magenta "$(printf '=%.0s' {1..50})\n"
    
    # 获取当前分支
    local current_branch=$(get_current_branch)
    if [ -z "$current_branch" ]; then
        print_colored red "无法确定当前分支"
        return 1
    fi
    
    print_colored blue "当前分支: $current_branch"
    
    # 检查是否有未提交的更改
    local status=$(git status --porcelain)
    if [ -z "$status" ]; then
        print_colored yellow "没有需要提交的更改"
        return 0
    fi
    
    print_colored blue "检测到以下更改:"
    echo "$status"
    
    # 提交更改
    read -p "输入提交信息 (留空使用默认信息): " commit_message
    if [ -z "$commit_message" ]; then
        commit_message="自动提交于 $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    print_colored blue "\n正在提交更改..."
    run_git_command add . || return 1
    run_git_command commit -m "$commit_message" || return 1
    
    # 获取远程最新更改（防止推送前有新的提交）
    print_colored blue "\n正在获取远程更新..."
    run_git_command fetch || return 1
    
    # 尝试变基
    print_colored blue "\n正在变基到远程最新版本..."
    if ! run_git_command rebase origin/$current_branch; then
        if [[ "$git_output" == *"CONFLICT"* ]]; then
            resolve_conflicts || return 1
        else
            print_colored red "变基失败"
            return 1
        fi
    fi
    
    # 推送到远程
    print_colored blue "\n正在推送到远程仓库..."
    run_git_command push origin $current_branch || return 1
    
    print_colored green "\n同步完成，可以安全切换电脑!"
    return 0
}

# 主函数
main() {
    # 检查是否在Git仓库中
    if [ ! -d .git ]; then
        print_colored red "错误: 当前目录不是Git仓库"
        exit 1
    fi
    
    print_colored cyan "多电脑Git同步工具"
    echo "1. 开始开发前同步 (拉取最新代码)"
    echo "2. 开发结束后同步 (推送更改到远程)"
    
    read -p "请选择操作 (1/2): " choice
    
    case $choice in
        1)
            if sync_before_start; then
                exit 0
            else
                exit 1
            fi
            ;;
        2)
            if sync_after_finish; then
                exit 0
            else
                exit 1
            fi
            ;;
        *)
            print_colored red "无效选择"
            exit 1
            ;;
    esac
}

# 执行主函数
main