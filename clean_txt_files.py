#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
========================================================
图片描述文件清除工具
========================================================

【功能说明】
这个程序用于清除由图片描述生成工具创建的文本文件(.txt)。
当你需要重新生成图片描述，或者想清除旧的描述文件时，
可以使用此工具来批量删除文本文件。

【使用方法】
1. 设置下方的全局变量:
   - TARGET_FOLDER: 要清除的单个文件夹名称（如"厨房"）
   - CLEAN_ALL_FOLDERS: 控制清除模式
     - 0: 只清除TARGET_FOLDER指定的文件夹中的文件
     - 1: 清除所有文件夹中的文件

2. 运行程序: python clean_txt_files.py

3. 程序会询问确认，输入'y'确认删除，输入其他取消操作

4. 程序将:
   - 删除指定文件夹中的所有.txt文件
   - 删除进度记录文件，使得下次运行描述生成工具时重新开始

【文件夹结构】
程序会处理以下结构中的文件:
picture/
  ├── 厨房/
  │   ├── 任意图片.png
  │   ├── 任意图片.txt  (将被删除)
  │   └── ...
  ├── 客厅/
  │   ├── 图片.png
  │   ├── 图片.txt  (将被删除)
  │   └── ...
  └── ...

【安全措施】
- 程序只会删除.txt文件，不会删除图片文件
- 执行前会要求确认，避免意外操作
- 会显示删除的文件列表，便于确认

【注意事项】
- 删除操作不可撤销，请谨慎确认
- 如果指定的文件夹不存在，程序会提示错误
- 可以反复运行此程序，不会有副作用
"""

import os
import shutil

# ====================== 全局配置参数 ======================

# 目标文件夹，当CLEAN_ALL_FOLDERS=0时生效
TARGET_FOLDER = "厨房"

# 控制清除模式：0=只清除单个文件夹，1=清除所有文件夹
CLEAN_ALL_FOLDERS = 0

# 基础目录，所有图片文件夹的上级目录
BASE_DIR = "picture"

# 进度文件名
PROGRESS_FILE = "progress.txt"
FOLDERS_PROGRESS_FILE = "folders_progress.txt"


# ====================== 函数定义 ======================

def list_all_folders():
    """获取BASE_DIR下的所有文件夹"""
    return [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]


def clean_folder(folder_name, is_single_mode=False):
    """
    清除指定文件夹中的所有.txt文件

    参数:
        folder_name: 文件夹名称
        is_single_mode: 是否为单文件夹模式，如果是则文件夹不存在时退出程序

    返回:
        tuple: (已清除文件数量, 是否成功)
    """
    folder_path = os.path.join(BASE_DIR, folder_name)

    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        if is_single_mode:  # 单文件夹模式
            print(f"错误: 文件夹 '{folder_name}' 不存在。请检查并更改 TARGET_FOLDER 变量后重试。")
            return 0, False
        else:  # 多文件夹模式
            print(f"警告: 文件夹 '{folder_name}' 不存在，已跳过")
            return 0, True  # 返回成功状态以继续处理其他文件夹

    count = 0
    try:
        # 删除所有.txt文件
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.txt'):
                file_path = os.path.join(folder_path, file_name)
                os.remove(file_path)
                count += 1
                print(f"已删除: {file_path}")

        # 删除进度文件（如果存在）
        progress_path = os.path.join(folder_path, PROGRESS_FILE)
        if os.path.exists(progress_path):
            os.remove(progress_path)
            print(f"已删除进度文件: {progress_path}")

        return count, True
    except Exception as e:
        print(f"清除文件夹 '{folder_name}' 时出错: {e}")
        if is_single_mode:  # 在单文件模式下，任何错误都应该终止程序
            return count, False
        return count, True  # 在多文件模式下，继续处理其他文件夹


def clean_all_folders():
    """
    清除所有文件夹中的.txt文件

    返回:
        tuple: (已清除的文件夹数量, 已清除的文件总数)
    """
    folders = list_all_folders()

    if not folders:
        print(f"警告: 在 {BASE_DIR} 中没有找到任何文件夹")
        return 0, 0

    folder_count = 0
    total_files = 0

    print(f"开始清除所有文件夹中的.txt文件，共 {len(folders)} 个文件夹...")

    for folder in folders:
        print(f"\n处理文件夹: {folder}")
        files_count, success = clean_folder(folder, is_single_mode=False)

        if success:
            folder_count += 1
            total_files += files_count
            print(f"文件夹 '{folder}' 已清除 {files_count} 个文件")

    # 删除总进度文件（如果存在）
    folders_progress_path = os.path.join(BASE_DIR, FOLDERS_PROGRESS_FILE)
    if os.path.exists(folders_progress_path):
        os.remove(folders_progress_path)
        print(f"\n已删除总进度文件: {folders_progress_path}")

    return folder_count, total_files


def clean_target_folder():
    """
    清除目标文件夹中的.txt文件

    返回:
        int: 已清除的文件数量，如果失败则返回-1
    """
    print(f"开始清除文件夹 '{TARGET_FOLDER}' 中的.txt文件...")
    files_count, success = clean_folder(TARGET_FOLDER, is_single_mode=True)

    if success:
        print(f"文件夹 '{TARGET_FOLDER}' 已清除 {files_count} 个文件")
        return files_count
    else:
        print(f"清除文件夹 '{TARGET_FOLDER}' 失败")
        return -1


# ====================== 主函数 ======================

def main():
    """主函数，根据全局变量设置执行清除操作"""
    # 检查基础目录是否存在
    if not os.path.exists(BASE_DIR):
        print(f"错误: 基础目录 '{BASE_DIR}' 不存在，请检查 BASE_DIR 变量设置")
        return False

    print("===== 图片描述文本文件清除工具 =====")
    print(f"基础目录: {BASE_DIR}")

    if CLEAN_ALL_FOLDERS == 1:
        print("模式: 清除所有文件夹")
        folder_count, total_files = clean_all_folders()
        print(f"\n清除完成! 已处理 {folder_count} 个文件夹，共删除 {total_files} 个文件")
        return True
    else:
        print(f"模式: 清除单个文件夹 '{TARGET_FOLDER}'")
        files_count = clean_target_folder()
        if files_count >= 0:
            print(f"\n清除完成! 共删除 {files_count} 个文件")
            return True
        else:
            print("操作未完成，请检查设置后重试")
            return False


if __name__ == "__main__":
    # 确认操作
    mode = "所有文件夹" if CLEAN_ALL_FOLDERS == 1 else f"文件夹 '{TARGET_FOLDER}'"
    confirmation = input(f"确定要删除{mode}中的所有.txt文件吗？(y/n): ")

    if confirmation.lower() == 'y':
        success = main()
        if not success:
            exit(1)
    else:
        print("操作已取消") 