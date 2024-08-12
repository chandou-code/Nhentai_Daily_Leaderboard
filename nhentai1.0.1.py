import concurrent.futures

import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

import queue


def get_html(page):
    today = datetime.now().strftime('%Y-%m-%d')
    directory = 'nhentais'
    file_path = os.path.join(directory, f'{today}_{page}.html')
    if os.path.exists(file_path):
        print(f"File '{file_path}' already exists. Skipping download.")
        return False

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('')

    url = f'https://nhentai.net/search/?q=+language%3A%22chinese%22&page={page}&sort=popular-today'

    # 设置 headers，包括 User-Agent 和 Cookie
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        'Cookie': 'csrftoken=c1H4KKNCTe5KSJofYshcXtGDVoyAlfXhss0VM0LDvtKqBCm97MGvZKcIvpfqPtr7'
    }
    proxies = {
        'http': 'http://localhost:7890',
        'https': 'http://localhost:7890',
    }
    print(f'请求:{url}')

    # 发送 GET 请求
    r = requests.get(url, headers=headers, proxies=proxies)

    # 打印状态码以确认请求是否成功
    print(r.status_code)
    text = r.text

    # 写入 HTML 内容到文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

    return True


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
    return img_tags
    # 使用 zip 函数同时遍历两个列表


def sanitize_filename(filename):
    # 只保留字母、数字、下划线和句点，其它字符都替换为下划线
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def get_picture(name, data_src, page):
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
    try:

        proxies = {
            'http': 'http://localhost:7890',
            'https': 'http://localhost:7890',
        }

        # 发送 GET 请求
        r = requests.get(data_src, headers=headers, proxies=proxies)
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

    # 新的 JavaScript 代码
    new_script_content = """
         document.querySelectorAll('.caption').forEach(div => {
            div.addEventListener('click', function() {
                const text = this.innerText;
                navigator.clipboard.writeText(text).then(() => {
                    alert('Text copied to clipboard!');
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                });
            });
        });
           function copyToClipboard(text) {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }

        // Add event listener to all links with class 'cover'
        document.addEventListener('DOMContentLoaded', () => {
            const links = document.querySelectorAll('a.cover');
            links.forEach(link => {
                link.addEventListener('click', function(event) {
                    event.preventDefault(); // Prevent the default action of the link

                    // Get the href attribute
                    const href = this.getAttribute('href');

                    // Create the full URL by concatenating the base URL with the href
                    const baseURL = 'https://nhentai.net';
                    const fullURL = baseURL + href;

                    // Copy the full URL to clipboard
                    copyToClipboard(fullURL);

                    // Optionally show an alert to indicate success
                    // alert('Link copied to clipboard: ' + fullURL);
                });
            });
        });
    """

    # 创建新的 <script> 标签
    new_script_tag = soup.new_tag('script')
    new_script_tag.string = new_script_content

    # 找到现有的 <script> 标签，并插入新的 <script> 标签
    existing_script_tags = soup.find_all('script')
    if existing_script_tags:
        last_script_tag = existing_script_tags[-1]
        last_script_tag.insert_after(new_script_tag)
    else:
        # 如果没有现有的 <script> 标签，则直接将新脚本添加到 body 的末尾
        soup.body.append(new_script_tag)

    # 将修改后的 HTML 转回字符串
    updated_html_content = str(soup)

    # 保存更新后的 HTML 内容
    write_html_to_file(file_path, updated_html_content)
    print("HTML 内容更新成功。")

def location_static(page):
    today = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join('nhentais', f'{today}_{page}.html')
    print(file_path)
    if not os.path.exists(file_path):
        print("文件未找到")
        return

    html_content = read_html_from_file(file_path)


    soup = BeautifulSoup(html_content, 'html.parser')

    for link in soup.find_all('link'):
        href = link.get('href')
        if 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome' in href:
            link['href'] = './static/all.min.css'
        elif 'https://static.nhentai.net/css/styles' in href:
            link['href'] = './static/styles.3880fca2c456.css'

    # for script in soup.find_all('script'):
    #     src = script.get('src')
        # if 'https://static.nhentai.net/js/scripts' in src:
        #     script['src'] = './static/scripts.ee1fea267e1e.js'

    # 将修改后的 HTML 转换为字符串
    new_html_content = str(soup)

    # 打印或保存新 HTML 内容

    # 将修改后的 HTML 转回字符串


    # 保存更新后的 HTML 内容
    write_html_to_file(file_path, new_html_content)
    print("HTML 内容更新成功2。")

def main():
    page = int(input('页数:'))
    for i in range(page):
        print(i + 1)
        if get_html(i + 1):
            tr_main(i + 1)
            change_to_location(i + 1)
            location_static(i + 1)
    y = input('end')


def debug():
    change_to_location(3)




def tr_main(page):
    task_queue = queue.Queue()
    # lists = []
    img_tags = get_src_from_file(page)
    for i in img_tags:
        # lists.append(i)
        data_src = i.get('data-src')
        dic1={
            'url':data_src,
            'page':page
        }
        task_queue.put(dic1)

    # timelogging.base_handled(lists)
    # 创建多线程池
    num_threads = 5  # 线程数
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # 提交任务给线程池执行
        while not task_queue.empty():
            task = task_queue.get()
            # print(task)
            executor.submit(task_function, task)

        # 等待所有任务完成
        executor.shutdown()


def task_function(img_tag):
    # print(img_tag)
    page=img_tag['page']
    url=img_tag['url']
    data_src =url
    # print(data_src)
    #
    print(f"Data-src: {data_src}")

    match = re.search(r'/galleries/(\d+)/', data_src)
    gallery_id = match.group(1)

    get_picture(gallery_id, data_src, page)
    print('---')  # 分隔不同的 img 和 name 标签





if __name__ == '__main__':
    # print(get_detain_picture('https://nhentai.net/g/523641/'))
    # print(get_html(3))
    # get_html(1)
    # tr_main(1)
    # change_to_location(1)
    # location_static(1)
    # location_static(2)
    # location_static(3)
    main()