# 图片描述生成工具集 / Image Description Generation Toolkit

## 项目介绍 / Project Introduction

这是一套用于自动处理图片并生成描述文本的工具集。主要用于图片的描述生成，支持批量处理多个文件夹中的图片，自动将不同格式的图片转换为统一格式，并通过AI技术生成精准的描述文本。

This is a toolkit for automatically processing images and generating descriptive text. It is primarily designed for describing architectural space images, supporting batch processing of images in multiple folders, automatically converting different image formats to a unified format, and generating accurate descriptive text through AI technology.

## 功能模块 / Functional Modules

### 1. 图片格式转换工具 / Image Format Conversion Tool

将picture目录中的所有图片转换为PNG格式，支持jpg、jpeg、png、gif、bmp、webp、tiff、tif等多种格式的转换。

Converts all images in the picture directory to PNG format, supporting conversion from various formats including jpg, jpeg, png, gif, bmp, webp, tiff, tif, etc.

#### 主要功能 / Main Features:

- 批量转换各种格式的图片为PNG格式
- 保留图片透明通道（如果存在）
- 多线程并行处理加速转换过程
- 自动删除转换后的原始文件

- Batch conversion of various image formats to PNG
- Preserve image transparency channel (if present)
- Multi-threaded parallel processing to accelerate conversion
- Automatically delete original files after conversion

#### 使用方法 / Usage:

```bash
python convert_to_png.py [目标目录路径/target directory path]
```

不指定目录时，默认处理"picture"目录。

If no directory is specified, the "picture" directory is processed by default.

### 2. 图片自动描述生成工具 / Automatic Image Description Generator

这个程序可以自动为图片生成文字描述，特别适合建筑空间图片的描述。程序会读取指定文件夹中的图片，通过人工智能识别图片内容，然后生成英文描述，并保存为同名的文本文件。

This program automatically generates text descriptions for images, particularly suitable for architectural space images. It reads images from specified folders, recognizes the image content through artificial intelligence, then generates English descriptions and saves them as text files with the same name.

#### 主要功能 / Main Features:

- 支持PNG、WEBP、JPEG、JPG等多种图片格式
- 批量处理单个或多个文件夹中的图片
- 智能排序处理（数字名称优先，按数值排序）
- 断点续传功能，中断后可从上次处理的位置继续

- Supports multiple image formats including PNG, WEBP, JPEG, JPG
- Batch processing of images in single or multiple folders
- Intelligent sorting (numeric names prioritized and sorted by value)
- Resume function, can continue from last processed position after interruption

#### 文件命名建议 / File Naming Suggestions:

程序支持任意文件名的PNG、WEBP、JPEG、JPG图片（如"12315123.png"或"safafaf.png"）
文件名排序规则：
  • 如果所有文件都是纯数字命名，则按照数值从小到大排序（例如：1, 2, 10, 100）；
  • 如果存在非数字命名，则纯数字文件名优先按数值排序排列在前，随后对非纯数字文件名按照字母表顺序排序（例如：1, 2, 3, a, b, c）。
为了确保按顺序处理，建议使用纯数字命名（如1.png, 2.png, 3.png）。

The program supports any filename for PNG, WEBP, JPEG, JPG images (such as "12315123.png" or "safafaf.png").
File name sorting rules:
  • If all files have pure numeric names, they are sorted by numerical value (e.g., 1, 2, 10, 100);
  • If non-numeric names exist, pure numeric filenames are prioritized and sorted by value first, followed by non-numeric filenames sorted alphabetically (e.g., 1, 2, 3, a, b, c).
For consistent processing order, it's recommended to use pure numeric naming (like 1.png, 2.png, 3.png).

#### 使用方法 / Usage:

```bash
python generate_picture_describe.py
```

通过修改脚本中的全局变量来配置处理模式：
- `CURRENT_FOLDER`: 要处理的单个文件夹名称
- `PROCESS_ALL_FOLDERS`: 是否处理所有文件夹

Configure the processing mode by modifying global variables in the script:
- `CURRENT_FOLDER`: Name of a single folder to process
- `PROCESS_ALL_FOLDERS`: Whether to process all folders

### 3. 图片描述文件清除工具 / Image Description File Cleaner

这个程序用于清除由图片描述生成工具创建的文本文件(.txt)。当你需要重新生成图片描述，或者想清除旧的描述文件时，可以使用此工具来批量删除文本文件。

This program is used to remove text files (.txt) created by the image description generation tool. When you need to regenerate image descriptions or clear old description files, you can use this tool to batch delete text files.

#### 主要功能 / Main Features:

- 批量删除指定文件夹中的所有.txt文件
- 支持单文件夹或所有文件夹模式
- 删除进度记录文件，使得下次运行描述生成工具时重新开始
- 安全确认机制，避免意外操作

- Batch deletion of all .txt files in specified folders
- Support for single folder or all folders mode
- Delete progress record files to restart the description generation tool
- Safe confirmation mechanism to avoid accidental operations

#### 使用方法 / Usage:

```bash
python clean_txt_files.py
```

通过修改脚本中的全局变量来配置处理模式：
- `TARGET_FOLDER`: 要清除的单个文件夹名称
- `CLEAN_ALL_FOLDERS`: 控制清除模式（0=只清除单个文件夹，1=清除所有文件夹）

Configure the processing mode by modifying global variables in the script:
- `TARGET_FOLDER`: Name of a single folder to clean
- `CLEAN_ALL_FOLDERS`: Control cleaning mode (0=clean single folder only, 1=clean all folders)

## 文件夹结构 / Folder Structure

程序处理以下结构中的文件:

The program processes files in the following structure:

```
picture/
  ├── 厨房/Kitchen/
  │   ├── 1.png
  │   ├── 2.png
  │   ├── 1.txt (生成的描述文件/generated description file)
  │   ├── 2.txt (生成的描述文件/generated description file)
  │   └── ...
  ├── 客厅/Living Room/
  │   ├── 1.png
  │   ├── 2.png
  │   └── ...
  └── ...
```

## 注意事项 / Notes

- 所有脚本默认处理"picture"目录，确保该目录存在
- 如需处理其他目录，请修改相应脚本中的`BASE_DIR`变量
- 删除文本文件的操作不可撤销，使用清除工具前请谨慎确认
- 程序使用讯飞星火API进行图片识别，确保网络连接正常

- All scripts process the "picture" directory by default, ensure this directory exists
- To process other directories, modify the `BASE_DIR` variable in the respective script
- The operation of deleting text files is irreversible, please confirm carefully before using the cleaning tool
- The program uses Xunfei Spark API for image recognition, ensure network connection is normal 