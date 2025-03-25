#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
========================================================
图片格式转换工具 / Image Format Conversion Tool
========================================================

【功能说明 / Function Description】
这个程序用于将picture目录中的所有图片转换为PNG格式。
支持多种常见图片格式，如jpg、jpeg、webp、gif、bmp等，
转换后会保留图片原有的透明通道（如果存在）。

This program is used to convert all images in the picture directory to PNG format.
It supports various common image formats such as jpg, jpeg, webp, gif, bmp, etc.,
and preserves the original transparency channel of the image (if it exists) after conversion.

【使用方法 / Usage】
1. 直接运行程序: python convert_to_png.py
   或指定目录: python convert_to_png.py [目标目录路径]

   Run the program directly: python convert_to_png.py
   Or specify a directory: python convert_to_png.py [target directory path]

2. 程序将 / The program will:
   - 遍历指定目录中的所有图片文件 / Traverse all image files in the specified directory
   - 自动将其转换为PNG格式 / Automatically convert them to PNG format
   - 删除原始文件（非PNG格式的文件） / Delete original files (non-PNG format files)
   - 显示转换进度和结果统计 / Display conversion progress and result statistics

【主要特点 / Main Features】
- 多线程并行处理，加速转换过程 / Multi-threaded parallel processing to accelerate conversion
- 支持递归处理子目录中的图片 / Support recursive processing of images in subdirectories
- 智能保留透明通道 / Intelligently preserve transparency channels
- 自动删除已转换的原始文件 / Automatically delete converted original files

【支持的图片格式 / Supported Image Formats】
- jpg, jpeg / JPEG format
- webp / WebP format
- gif / GIF format
- bmp / BMP format
- tiff, tif / TIFF format
- png (已经是PNG格式的文件会被跳过) / PNG (files already in PNG format will be skipped)

【注意事项 / Notes】
- 请在执行前确保图片文件已备份 / Make sure image files are backed up before execution
- 转换过程不可逆，原始文件（非PNG）将被删除 / The conversion is irreversible, original files (non-PNG) will be deleted
- 需要安装PIL/Pillow库 / PIL/Pillow library needs to be installed
"""

import os
import sys
from pathlib import Path
import shutil
from PIL import Image
import concurrent.futures

def convert_image_to_png(source_path, verbose=True):
    """
    将单个图片转换为PNG格式
    Convert a single image to PNG format
    """
    try:
        # 检查源文件是否存在 / Check if source file exists
        if not os.path.exists(source_path):
            if verbose:
                print(f"文件不存在: {source_path} / File doesn't exist")
            return False, "文件不存在 / File doesn't exist"
            
        # 创建目标路径 (替换扩展名为.png) / Create target path (replace extension with .png)
        target_path = str(Path(source_path).with_suffix('.png'))
        
        # 如果目标文件已存在且与源文件相同，则跳过 / Skip if target file already exists and is the same as source
        if source_path == target_path:
            if verbose:
                print(f"文件已经是PNG格式: {source_path} / File is already in PNG format")
            return True, "已经是PNG格式 / Already PNG"
            
        # 打开图片 / Open the image
        img = Image.open(source_path)
        
        # 如果图片有透明通道，保留它；否则转换为RGB / If image has transparency, preserve it; otherwise convert to RGB
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            # 保留透明通道 / Preserve transparency channel
            img = img.convert('RGBA')
        else:
            # 转换为RGB / Convert to RGB
            img = img.convert('RGB')
            
        # 保存为PNG / Save as PNG
        img.save(target_path, 'PNG')
        
        # 验证转换是否成功 / Verify if conversion was successful
        if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
            if verbose:
                print(f"✓ 转换成功: {source_path} -> {target_path} / Conversion successful")
                
            # 如果源文件不是PNG文件，可以选择删除它 / If source file is not a PNG file, optionally delete it
            if Path(source_path).suffix.lower() != '.png':
                try:
                    os.remove(source_path)
                    if verbose:
                        print(f"  已删除原文件 / Original file deleted")
                except Exception as e:
                    if verbose:
                        print(f"  无法删除原文件: {str(e)} / Cannot delete original file")
                
            return True, "转换成功 / Conversion successful"
        else:
            if verbose:
                print(f"✗ 转换失败: {source_path} / Conversion failed")
            return False, "转换失败 / Conversion failed"
            
    except Exception as e:
        if verbose:
            print(f"✗ 处理图片时出错: {source_path} - {str(e)} / Error processing image")
        return False, f"错误: {str(e)} / Error: {str(e)}"

def process_directory(directory_path, recursive=True, verbose=True):
    """
    处理目录中的所有图片
    Process all images in a directory
    """
    # 确保目录存在 / Ensure directory exists
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        print(f"错误: 目录不存在: {directory_path} / Error: Directory doesn't exist")
        return
        
    # 图片文件扩展名 / Image file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
    
    # 收集要处理的文件 / Collect files to process
    image_files = []
    
    # 遍历目录 / Traverse directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            extension = os.path.splitext(file)[1].lower()
            
            # 检查是否是图片文件 / Check if it's an image file
            if extension in image_extensions:
                image_files.append(file_path)
                
        # 如果不递归，则在第一层后停止 / If not recursive, stop after the first level
        if not recursive:
            break
    
    # 统计信息 / Statistics
    total_images = len(image_files)
    successful = 0
    failed = 0
    skipped = 0
    
    if verbose:
        print(f"\n找到 {total_images} 个图片文件 / Found {total_images} image files")
    
    # 使用线程池加速处理 / Use thread pool to speed up processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, os.cpu_count() * 2)) as executor:
        # 创建转换任务 / Create conversion tasks
        future_to_path = {
            executor.submit(convert_image_to_png, path, verbose): path 
            for path in image_files
        }
        
        # 处理结果 / Process results
        for i, future in enumerate(concurrent.futures.as_completed(future_to_path), 1):
            path = future_to_path[future]
            success, message = future.result()
            
            if success:
                if "已经是PNG格式" in message:
                    skipped += 1
                else:
                    successful += 1
            else:
                failed += 1
                
            if verbose:
                print(f"进度: {i}/{total_images} ({i/total_images*100:.1f}%) / Progress")
    
    # 显示最终统计 / Show final statistics
    print("\n转换完成! / Conversion completed!")
    print(f"总图片数: {total_images} / Total images")
    print(f"成功转换: {successful} / Successfully converted")
    print(f"已是PNG格式: {skipped} / Already PNG")
    print(f"转换失败: {failed} / Failed")

def main():
    """
    主函数
    Main function
    """
    # 确定要处理的目录 / Determine directory to process
    picture_dir = "picture"
    
    # 检查命令行参数 / Check command line arguments
    if len(sys.argv) > 1:
        picture_dir = sys.argv[1]
    
    print(f"图片格式转换工具 - 将所有图片转换为PNG格式 / Image Format Conversion Tool")
    print(f"目标目录: {os.path.abspath(picture_dir)} / Target directory")
    
    # 确认操作 / Confirm operation
    if len(sys.argv) <= 1:  # 没有明确指定目录时请求确认 / Request confirmation when directory is not explicitly specified
        confirm = input("是否继续? (y/n) / Continue? (y/n): ")
        if confirm.lower() not in ('y', 'yes'):
            print("操作已取消 / Operation canceled")
            return
    
    # 处理目录 / Process directory
    process_directory(picture_dir, recursive=True)

if __name__ == "__main__":
    main() 