import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime


def get_html(page):
    today = datetime.now().strftime('%Y-%m-%d')
    directory = 'nhentais'
    file_path = os.path.join(directory, f'{today}_{page}.html')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('')



    url = f'https://nhentai.net/search/?q=+language%3A%22chinese%22&page={page}&sort=popular-today'

    # 设置 headers，包括 User-Agent 和 Cookie
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        'Cookie': 'csrftoken=c1H4KKNCTe5KSJofYshcXtGDVoyAlfXhss0VM0LDvtKqBCm97MGvZKcIvpfqPtr7'
    }
    print(f'请求:{url}')
    # 发送 GET 请求
    r = requests.get(url, headers=headers)

    # 打印状态码以确认请求是否成功
    print(r.status_code)
    text = r.text

    # 写入 HTML 内容到文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

    return text


def read_html_from_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        return file.read()


def get_src_from_file(page):
    today = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join('nhentais', f'{today}_{page}.html')
    if not os.path.exists(f'nhentais/{today}_{page}'):
        os.makedirs(f'nhentais/{today}_{page}')


    html_content = read_html_from_file(file_path)

    # 解析 HTML 内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找所有具有特定 class 的 img 标签
    img_tags = soup.find_all('img', class_='lazyload')
    # 使用 find_all 查找 class 为 caption 的 div 标签
    name_tags = soup.find_all('div', class_='caption')

    # 使用 zip 函数同时遍历两个列表
    for img_tag, name_tag in zip(img_tags, name_tags):
        # 提取 img 标签的 src 和 data-src 属性

        data_src = img_tag.get('data-src')

        # 提取 name 标签的文本内容
        name = name_tag.get_text(strip=True)

        # print(f"Name: {name}")
        print(f"Data-src: {data_src}")

        match = re.search(r'/galleries/(\d+)/', data_src)
        gallery_id = match.group(1)

        get_picture(gallery_id, data_src)
        print('---')  # 分隔不同的 img 和 name 标签


def sanitize_filename(filename):
    # 只保留字母、数字、下划线和句点，其它字符都替换为下划线
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def get_picture(name, data_src):
    global r
    today = datetime.now().strftime('%Y-%m-%d')
    directory_path = os.path.join('nhentais', f'{today}_{page}')
    file_path = os.path.join(directory_path, f'{sanitize_filename(name)}.jpg')

    # 如果文件已经存在，则直接返回
    if os.path.exists(file_path):
        print(f"File '{file_path}' already exists. Skipping download.")
        return

    # 设置 headers，包括 User-Agent 和 Cookie
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',

    }

    # 发送 GET 请求
    try:r = requests.get(data_src, headers=headers)
    except:
        pass

    # 打印状态码以确认请求是否成功
    print(r.status_code)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # 确保请求成功
    if r.status_code == 200:
        # 清理文件名
        sanitized_name = sanitize_filename(name)
        file_path = os.path.join(directory_path, f'{sanitized_name}.jpg')

        # 以二进制模式写入文件
        with open(file_path, 'wb') as file:
            file.write(r.content)
        print(f"保存:{file_path}")
    else:
        print("Failed to retrieve the image.")





def write_html_to_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def change_to_location(page):
    today = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join('nhentais', f'{today}_{page}.html')
    print(file_path)
    if not os.path.exists(file_path):
        print("文件未找到")
        return

    html_content = read_html_from_file(file_path)

    # 解析 HTML 内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找所有具有特定 class 的 img 标签
    img_tags = soup.find_all('img', class_='lazyload')
    # 使用 find_all 查找 class 为 caption 的 div 标签
    name_tags = soup.find_all('div', class_='caption')

    for img_tag in img_tags:
        data_src = img_tag.get('data-src')
        if data_src:
            match = re.search(r'/galleries/(\d+)/', data_src)
            if match:
                gallery_id = f'{today}_{page}/{match.group(1)}.jpg'
                img_tag['src'] = gallery_id  # 更新 data-src 属性

    # 将修改后的 HTML 转回字符串
    updated_html_content = str(soup)

    # 保存更新后的 HTML 内容
    write_html_to_file(file_path, updated_html_content)
    print("'HTML 内容更新成功。")






if __name__ == '__main__':
    page=int(input('页数:'))
    get_html(page)
    get_src_from_file(page)
    change_to_location(page)
