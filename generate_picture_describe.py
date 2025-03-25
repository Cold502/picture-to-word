#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
========================================================
图片自动描述生成工具 / Automatic Image Description Generator
========================================================

【功能说明 / Function Description】
这个程序可以自动为图片生成文字描述，特别适合建筑空间图片的描述。
程序会读取指定文件夹中的图片，通过人工智能识别图片内容，
然后生成英文描述，并保存为同名的文本文件。

This program automatically generates text descriptions for images, particularly 
suitable for architectural space images. It reads images from specified folders, 
recognizes the image content through artificial intelligence, then generates 
English descriptions and saves them as text files with the same name.

【使用方法 / Usage】
1. 设置下方的全局变量 / Set the global variables below:
   - CURRENT_FOLDER: 要处理的单个文件夹名称（如"厨房"）/ Name of a single folder to process (e.g., "Kitchen")
   - PROCESS_ALL_FOLDERS: 是否处理所有文件夹 / Whether to process all folders
     - True: 处理所有文件夹 / Process all folders
     - False: 只处理CURRENT_FOLDER指定的文件夹 / Only process the folder specified by CURRENT_FOLDER

2. 运行程序 / Run the program: python generate_picture_describe.py

3. 程序将 / The program will:
   - 读取图片文件夹中的图片（按文件名排序）/ Read images from the folder (sorted by filename)
   - 调用讯飞星火API识别图片内容 / Call Xunfei Spark API to recognize image content
   - 生成对应的英文描述，保存为同名的.txt文件 / Generate corresponding English descriptions and save as .txt files
   - 处理过程会显示在屏幕上 / The processing progress will be displayed on screen

【文件夹结构 / Folder Structure】
图片应按以下结构放置 / Images should be placed in the following structure:
picture/
  ├── 厨房/Kitchen/
  │   ├── 1.png
  │   ├── 2.png
  │   └── ...
  ├── 客厅/Living Room/
  │   ├── 1.png
  │   └── ...
  └── ...

【文件命名建议 / File Naming Suggestions】
程序支持任意文件名的PNG、WEBP、JPEG、JPG图片（如"12315123.png"或"safafaf.png"）
文件名排序规则：
  • 如果所有文件都是纯数字命名，则按照数值从小到大排序（例如：1, 2, 10, 100）；
  • 如果存在非数字命名，则纯数字文件名优先按数值排序排列在前，随后对非纯数字文件名按照字母表顺序排序（例如：1, 2, 3, a, b, c）。
为了确保按顺序处理，建议使用纯数字命名（如1.png, 2.png, 3.png）
程序会自动检测文件命名情况并给出相应提示

The program supports any filename for PNG, WEBP, JPEG, JPG images (such as "12315123.png" or "safafaf.png")
File name sorting rules:
  • If all files have pure numeric names, they are sorted by numerical value (e.g., 1, 2, 10, 100);
  • If non-numeric names exist, pure numeric filenames are prioritized and sorted by value first, followed by non-numeric filenames sorted alphabetically (e.g., 1, 2, 3, a, b, c).
For consistent processing order, it's recommended to use pure numeric naming (like 1.png, 2.png, 3.png)
The program will automatically detect file naming patterns and provide appropriate prompts

【断点续传 / Resume Function】
如果程序中断，再次运行时会自动从上次处理的地方继续，
不会重复处理已经生成描述的图片。

If the program is interrupted, it will automatically continue from where it left off when run again,
without reprocessing images that have already been described.

【注意事项 / Notes】
- 图片文件必须是支持的格式: PNG, WEBP, JPEG, JPG / Image files must be in supported formats
- 图片文件可以是任意名称，会按照名称排序处理 / Image files can have any name and will be processed in order by name
- 需要连接网络访问星火AI服务 / Internet connection is required to access the Xunfei Spark AI service
"""

import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket  # 使用websocket_client
import os
import time

# 全局配置参数
appid = "3c571b44"  # 填写控制台中获取的 APPID 信息
api_secret = "NmNjZWZmYWE1YTFiODYyYmMwZTRiMDI0"  # 填写控制台中获取的 APISecret 信息
api_key = "797b6f8d7ba5f1fe84e345a57a32385a"  # 填写控制台中获取的 APIKey 信息
imageunderstanding_url = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"  # 云端环境的服务地址

# 全局变量控制文件夹和处理
CURRENT_FOLDER = "厨房"  # 当前处理的文件夹，仅在单文件夹模式有效
PROCESS_ALL_FOLDERS = True  # 设为True时处理所有文件夹，设为False时只处理CURRENT_FOLDER
BASE_DIR = "picture"  # 基础目录，所有图片文件夹的上级目录
FOLDERS_PROGRESS_FILE = "folders_progress.txt"  # 记录已处理的文件夹

# 提示词作为全局变量
PROMPT_TEMPLATE = "对下面图片进行描述（使用英文回答）,自然语言的形式列出,不要分点列出,内容要求精简一些,对于图片的的描述一定要准确,这张图片的主题是{folder_name}, 给你举个例子：A pristine hallway with a white ceiling, walls, and doors, featuring grey tiled flooring and black door handles. Linear lighting accents the ceiling, leading to a blue-tinted glass door at the end. 这种形式对张图片进行描述,一定要对图片进行准确描述,100-150个单词左右"

# 初始全局答案变量
answer = ""
text = []


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, imageunderstanding_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(imageunderstanding_url).netloc
        self.path = urlparse(imageunderstanding_url).path
        self.ImageUnderstanding_url = imageunderstanding_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数,生成url
        url = self.ImageUnderstanding_url + '?' + urlencode(v)
        # print(url)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释,比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, one, two):
    print(" ")


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, question=ws.question))
    ws.send(data)


# 收到websocket消息的处理
def on_message(ws, message):
    # print(message)
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        print(content, end="")
        global answer
        answer += content
        # print(1)
        if status == 2:
            ws.close()


def gen_params(appid, question):
    """
    通过appid和用户的提问来生成请参数
    """

    data = {
        "header": {
            "app_id": appid
        },
        "parameter": {
            "chat": {
                "domain": "image",
                "temperature": 0.5,
                "top_k": 4,
                "max_tokens": 2028,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }

    return data


def main(appid, api_key, api_secret, imageunderstanding_url, question):
    global answer
    answer = ""
    wsParam = Ws_Param(appid, api_key, api_secret, imageunderstanding_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    # ws.imagedata = imagedata
    ws.question = question
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return answer


def getText(role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text


def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(text):
    # print("text-content-tokens:", getlength(text[1:]))
    while (getlength(text[1:]) > 8000):  # 如果长度大于8000,则删除text[1]
        del text[1]
    return text


def get_progress_file(folder_path):
    """返回进度文件的路径"""
    return os.path.join(folder_path, "progress.txt")


def read_progress(progress_file):
    """读取已处理的图片记录"""
    if not os.path.exists(progress_file):
        return set()

    with open(progress_file, 'r') as f:
        processed = set(line.strip() for line in f if line.strip())
    return processed


def update_progress(progress_file, filename):
    """更新已处理的图片记录"""
    with open(progress_file, 'a') as f:
        f.write(f"{filename}\n")


def read_folders_progress():
    """读取已处理的文件夹记录"""
    progress_file = os.path.join(BASE_DIR, FOLDERS_PROGRESS_FILE)
    if not os.path.exists(progress_file):
        return set()

    with open(progress_file, 'r') as f:
        processed = set(line.strip() for line in f if line.strip())
    return processed


def update_folders_progress(folder_name):
    """更新已处理的文件夹记录"""
    progress_file = os.path.join(BASE_DIR, FOLDERS_PROGRESS_FILE)
    with open(progress_file, 'a') as f:
        f.write(f"{folder_name}\n")


def get_sorted_image_files(folder_path):
    """获取文件夹中的所有图片文件(支持png, webp, jpeg, jpg)并排序
    排序规则：纯数字的文件名按照数字从小到大排序，非纯数字的文件名按照字母表顺序排序，在排序后纯数字名称排在前面。"""
    valid_ext = ('.png', '.webp', '.jpeg', '.jpg')
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_ext)]

    # 按规则排序: 纯数字文件名按数值排序，非纯数字按字母排序，纯数字排在前面
    image_files.sort(key=lambda x: (0, int(os.path.splitext(x)[0])) if os.path.splitext(x)[0].isdigit() else (1, os.path.splitext(x)[0].lower()))

    return image_files


def is_txt_file_valid(txt_path):
    """检查txt文件是否存在且非空"""
    if not os.path.exists(txt_path):
        return False

    with open(txt_path, 'r') as f:
        content = f.read().strip()

    return len(content) > 0


def get_last_processed_image(folder_path):
    """获取最后一个已处理的图片文件名（不带扩展名）"""
    image_files = get_sorted_image_files(folder_path)

    if not image_files:
        return None

    # 检查是否所有图片都有对应的有效txt文件
    for img_file in reversed(image_files):
        base_name = os.path.splitext(img_file)[0]
        txt_file = base_name + ".txt"
        txt_path = os.path.join(folder_path, txt_file)

        if is_txt_file_valid(txt_path):
            return base_name

    return None


def is_folder_completed(folder_path):
    """检查文件夹是否已完成处理（所有png文件都有对应的非空txt）"""
    image_files = get_sorted_image_files(folder_path)

    if not image_files:
        return True  # 没有图片的文件夹视为已完成

    # 检查所有图片是否都有对应的有效txt文件
    for img_file in image_files:
        base_name = os.path.splitext(img_file)[0]  # 分割文件名和扩展名的函数 , 返回包含两个元素的元组 (root, ext)
        txt_file = base_name + ".txt"
        txt_path = os.path.join(folder_path, txt_file)

        if not is_txt_file_valid(txt_path):
            return False  # 如果有任何一张图片没有有效的txt文件，则未完成

    return True  # 所有图片都有对应的有效txt文件


def check_filename_format(folder_path):
    """检查文件夹中的图片文件命名方式，判断是否使用简单的数字命名

    参数:
        folder_path: 文件夹路径

    返回:
        bool: 是否采用数字命名
        list: 非数字命名的文件列表（最多5个）
    """
    valid_ext = ('.png', '.webp', '.jpeg', '.jpg')
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_ext)]

    # 检查是否都是数字命名的
    non_numeric_files = []
    for img_file in image_files:
        base_name = os.path.splitext(img_file)[0]
        if not base_name.isdigit():
            non_numeric_files.append(img_file)
            if len(non_numeric_files) >= 5:
                break

    # 如果所有文件都是数字命名的，返回True
    return len(non_numeric_files) == 0, non_numeric_files


def process_folder(folder_name):
    """处理单个文件夹中的所有图片"""
    global text
    folder_path = os.path.join(BASE_DIR, folder_name)

    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        if not PROCESS_ALL_FOLDERS:  # 单文件夹模式
            print(f"错误: 文件夹 '{folder_name}' 不存在。请检查并更改 CURRENT_FOLDER 变量后重试。")
            return False  # 返回False表示处理失败
        else:  # 多文件夹模式
            print(f"警告: 文件夹 '{folder_name}' 不存在，已跳过")
            return True  # 返回True表示处理完成（虽然是跳过）

    # 检查文件夹中的文件命名方式
    is_numeric_naming, non_numeric_files = check_filename_format(folder_path)
    if not is_numeric_naming:
        print(f"注意: 文件夹 '{folder_name}' 中存在非纯数字命名的图片文件")
        print("发现非数字命名的文件: " + ", ".join(non_numeric_files[:5]) +
              ("..." if len(non_numeric_files) > 5 else ""))
        print("程序可以处理任意长度的数字或字母文件名，但处理顺序会有所不同：")
        print("- 全部是纯数字命名时：按数值大小排序（1, 2, 10, 100...）")
        print("- 存在非数字命名时：按字符串排序（1, 10, 100, 2...）")
        print("如果您需要特定的处理顺序，建议使用纯数字命名（如1.png, 2.png）并确保所有文件都采用此命名方式")
        print("-" * 50)

    # 检查文件夹是否已完成处理
    if is_folder_completed(folder_path):
        print(f"文件夹 {folder_name} 已完全处理，跳过")
        return True

    # 获取最后一个已处理的图片文件名（不带扩展名）
    last_processed = get_last_processed_image(folder_path)

    # 获取文件夹中的所有PNG图片，并排序
    image_files = get_sorted_image_files(folder_path)

    if last_processed:
        print(f"开始处理 {folder_name} 文件夹中的图片，从 {last_processed} 之后开始...")
    else:
        print(f"开始处理 {folder_name} 文件夹中的所有图片...")

    # 标记是否找到上次处理的位置
    found_last_position = last_processed is None

    for image_file in image_files:
        # 获取当前图片的基本文件名（不带扩展名）
        current_base = os.path.splitext(image_file)[0]

        # 如果还没找到上次处理的位置且当前不是上次处理的图片，继续查找
        if not found_last_position:
            if current_base != last_processed:
                print(f"图片 {image_file} 已处理，跳过")
                continue
            else:
                # 找到了上次处理的位置，标记已找到，但跳过这个图片（因为已处理）
                found_last_position = True
                print(f"图片 {image_file} 已处理，跳过")
                continue

        # 图片路径
        image_path = os.path.join(folder_path, image_file)

        # 输出文件路径 (将.png替换为.txt)
        output_file = os.path.join(folder_path, current_base + '.txt')

        try:
            print(f"处理图片: {image_file}")
            # 读取图片
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # 清除之前的对话
            text = []

            # 设置带有文件夹名称的提示词
            prompt = PROMPT_TEMPLATE.format(folder_name=folder_name)
            print(f"使用提示词: {prompt[:50]}...")  # 输出部分提示词以验证文件夹名是否正确传入

            # 添加图片到对话
            image_base64 = str(base64.b64encode(image_data), 'utf-8')
            text.append({"role": "user", "content": image_base64, "content_type": "image"})

            # 添加提示词
            question = checklen(getText("user", prompt))

            # 调用API获取描述
            result = main(appid, api_key, api_secret, imageunderstanding_url, question)

            # 保存结果到文件
            with open(output_file, 'w') as f:
                f.write(result)

            print(f"已保存描述到: {output_file}")

            # 等待一下，避免过快请求
            time.sleep(1)

        except Exception as e:
            print(f"处理图片 {image_file} 时出错: {e}")

    print(f"{folder_name} 文件夹中的所有图片处理完成")
    return True  # 表示处理成功完成


def process_all_folders():
    """处理所有文件夹，按文件夹名称顺序从头开始处理"""
    # 获取所有文件夹并排序
    folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
    folders.sort()  # 按文件夹名称排序

    if not folders:
        print(f"警告: 在 {BASE_DIR} 中没有找到任何文件夹")
        return

    print(f"开始处理所有文件夹，共 {len(folders)} 个文件夹")

    for folder in folders:
        # 检查文件夹是否已完成处理
        folder_path = os.path.join(BASE_DIR, folder)
        if is_folder_completed(folder_path):
            print(f"文件夹 {folder} 已完全处理，跳过")
            continue

        # 处理文件夹
        print(f"开始处理文件夹: {folder}")
        process_folder(folder)

        print(f"已完成处理文件夹: {folder}")

    print("所有文件夹处理完成")


if __name__ == '__main__':
    # 检查基础目录是否存在
    if not os.path.exists(BASE_DIR):
        print(f"错误: 基础目录 '{BASE_DIR}' 不存在，请检查 BASE_DIR 变量设置")
        exit(1)

    # 根据PROCESS_ALL_FOLDERS变量决定处理模式
    if PROCESS_ALL_FOLDERS:
        # 处理所有文件夹模式，不受CURRENT_FOLDER影响
        process_all_folders()
    else:
        # 单文件夹模式，只处理CURRENT_FOLDER指定的文件夹
        print(f"单文件夹模式，处理: {CURRENT_FOLDER}")
        success = process_folder(CURRENT_FOLDER)
        if not success:
            print("处理中止：请检查并修改设置后重试")
            exit(1)

