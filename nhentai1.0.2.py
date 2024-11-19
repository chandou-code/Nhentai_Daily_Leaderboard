import concurrent.futures

import re
import time

import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

import queue



def read_config_from_file():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config

def get_html(page):
    today = datetime.now().strftime('%Y-%m-%d')
    directory = 'nhentais'
    file_path = os.path.join(directory, f'{today}_{page}.html')

    if os.path.exists(file_path):
        print(f"File '{file_path}' already exists. Skipping download.")
        return False

    url = f'https://nhentai.net/search/?q=+language%3A%22chinese%22&page={page}&sort=popular-today'
    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
    headers = {
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Cookie': 'csrftoken=c1H4KKNCTe5KSJofYshcXtGDVoyAlfXhss0VM0LDvtKqBCm97MGvZKcIvpfqPtr7',
        'Pragma': 'no-cache',
        'Sec-CH-UA': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
    }

    retries = read_config_from_file()['times']
    for attempt in range(retries):
        try:
            time.sleep(read_config_from_file()['sleep'])
            print(f'请求:{url}')
            r = requests.get(url, headers=headers, proxies=proxies)
            print(r.status_code)
            if r.status_code == 200:
                text = r.text

                if not os.path.exists(directory):
                    os.makedirs(directory)

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text)

                return True
            else:
                print(f"Failed to retrieve the HTML. Status code: {r.status_code}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")

        # time.sleep(1)  # 1

    print("Exceeded maximum retries. Failed to retrieve the HTML.")
    return False

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
    today = datetime.now().strftime('%Y-%m-%d')
    directory_path = os.path.join('nhentais', f'{today}_{page}')
    file_path = os.path.join(directory_path, f'{sanitize_filename(name)}.jpg')

    if os.path.exists(file_path):
        print(f"File '{file_path}' already exists. Skipping download.")
        return
    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
    headers = {
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Accept-Charset': 'utf-8',
        'Cache-Control': 'no-cache',
        'Cookie': 'csrftoken=c1H4KKNCTe5KSJofYshcXtGDVoyAlfXhss0VM0LDvtKqBCm97MGvZKcIvpfqPtr7',
        'Pragma': 'no-cache',
        'Sec-CH-UA': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
    }

    retries = read_config_from_file()['times']
    for attempt in range(retries):
        try:
            time.sleep(read_config_from_file()['sleep'])
            r = requests.get(data_src, headers = headers, proxies = proxies)
            if r.status_code == 200:
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)

                sanitized_name = sanitize_filename(name)
                file_path = os.path.join(directory_path, f'{sanitized_name}.jpg')

                with open(file_path, 'wb') as file:
                    file.write(r.content)
                print(f"保存:{file_path}")
                return
            else:
                print(f"Failed to retrieve the image. Status code: {r.status_code}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")

        # time.sleep(1)  # 等待2秒后重试

    # 记录失败的 URL 到 save.config
    save_failed_url(data_src, name, page)
import json
def save_failed_url(url, name, page):
    failed_urls = load_failed_urls()
    failed_urls.append({
        'url': url,
        'name': name,
        'page': page
    })
    try:
        with open('save.config', 'w') as f:
            json.dump(failed_urls, f, indent=4)
    except IOError as e:
        print(f"Error saving failed URLs: {e}")

def load_failed_urls():
    if os.path.exists('save.config'):
        try:
            with open('save.config', 'r') as f:
                content = f.read()
                if content.strip() == "":  # 检查文件是否为空
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading failed URLs: {e}")
            return []
    return []

def retry_failed_urls():
    failed_urls = load_failed_urls()
    for entry in failed_urls:
        print(f"Retrying: {entry['url']}")
        get_picture(entry['name'], entry['url'], entry['page'])
    # 清空或重置失败记录
    open('save.config', 'w').close()


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
    title = soup.find('title')
    title.string = file_path
    print(title)
    for script in soup.find_all('script', src=True):
        script['src']='./static/scripts.ee1fea267e1e.js'




    new_html_content = str(soup)

    write_html_to_file(file_path, new_html_content)
    print("HTML 内容更新成功2。")

def location_next_page(page):
    today = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join('nhentais', f'{today}_{page}.html')
    print(file_path)
    if not os.path.exists(file_path):
        print("文件未找到")
        return

    html_content = read_html_from_file(file_path)


    # 使用 BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(html_content, 'lxml')

    # 选择 <section> 元素
    section = soup.find('section', class_='pagination')

    if section:
        # 遍历所有 <a> 标签
        for link in section.find_all('a', class_='page'):
            # 提取文本作为页面号
            page_number = link.get_text()
            # 更新 href 属性
            new_href = f"{today}_{page_number}.html"
            link['href'] = new_href

        # 打印更新后的 <section> 元素
        # print("更新后的 <section> 元素：")
        # print(section.prettify())
        new_html_content = str(soup)
        write_html_to_file(file_path, new_html_content)
    else:
        print("没有找到 <section> 元素。")

def main():
    page = int(input('页数:'))
    for i in range(page):
        print(i + 1)
        if get_html(i + 1):
            single(i + 1)
            change_to_location(i + 1)
            location_static(i + 1)
            location_next_page(i + 1)
    y = input('end')




def single(page):
    img_tags = get_src_from_file(page)
    for i in img_tags:
        # print('i',i)
        data_src = i.get('data-src')
        print(data_src)
        #
        print(f"Data-src: {data_src}")

        match = re.search(r'/galleries/(\d+)/', data_src)
        gallery_id = match.group(1)

        get_picture(gallery_id, data_src, page)

def tr_main(page):
    task_queue = queue.Queue()
    # lists = []
    img_tags = get_src_from_file(page)
    for i in img_tags:
        # lists.append(i)
        data_src = i.get('data-src')
        dic1 = {
            'url': data_src,
            'page': page
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
            time.sleep(1.2)
            executor.submit(task_function, task)

        # 等待所有任务完成
        executor.shutdown()


def task_function(img_tag):
    # print(img_tag)
    page = img_tag['page']
    url = img_tag['url']
    data_src = url
    # print(data_src)
    #
    print(f"Data-src: {data_src}")

    match = re.search(r'/galleries/(\d+)/', data_src)
    gallery_id = match.group(1)

    get_picture(gallery_id, data_src, page)
    # print('---')  # 分隔不同的 img 和 name 标签

# def debugs():
#
#     headers = {
#         'Accept-Encoding': 'gzip, deflate, br, zstd',
#         'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
#         'Cache-Control': 'no-cache',
#         'Cookie': 'csrftoken=c1H4KKNCTe5KSJofYshcXtGDVoyAlfXhss0VM0LDvtKqBCm97MGvZKcIvpfqPtr7',
#         'Pragma': 'no-cache',
#         'Sec-CH-UA': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
#         'Sec-CH-UA-Mobile': '?0',
#         'Sec-CH-UA-Platform': '"Windows"',
#         'Sec-Fetch-Dest': 'document',
#         'Sec-Fetch-Mode': 'navigate',
#         'Sec-Fetch-Site': 'none',
#         'Sec-Fetch-User': '?1',
#         'Upgrade-Insecure-Requests': '1',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
#     }
#     url = f'https://nhentai.net/search/?q=+language%3A%22chinese%22&page=1&sort=popular-today'
#     r = requests.get(url, headers=headers)
#     print(r.text)
if __name__ == '__main__':

    main()

