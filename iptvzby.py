import time
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import re
import os
import threading
from queue import Queue
from datetime import datetime
import replace
import fileinput

#  获取远程港澳台直播源文件
url = "https://raw.gitcode.com/frxz751113/1/raw/main/IPTV/ott移动v4.txt"          #源采集地址
r = requests.get(url)
open('ott移动v4.txt','wb').write(r.content)         #打开源文件并临时写入

keywords = [',', 'http']  # 需要提取的关键字列表 8M1080
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('ott移动v4.txt', 'r', encoding='utf-8') as file, open('TW.txt', 'w', encoding='utf-8') as TW:
    TW.write('\n央视/随时失效,#genre#\n')
    for line in file:
      if '央视/随时失效,#genre#' not in line:  #设定含固定行不提取
       if re.search(pattern, line):  # 如果行中有任意关键字
          TW.write(line)  # 将该行写入输出文件

# 读取要合并的香港频道和台湾频道文件
file_contents = []
file_paths = ["TW.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)
# 生成合并后的文件
with open("GAT.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))


# 扫源测绘空间地址
# 搜素关键词："iptv/live/zh_cn.js" && country="CN" && region="Hunan" && city="changsha"
#            "iptv/live/zh_cn.js" && country="CN" && region="Guangxi Zhuangzu" && port="8181"
# 搜素关键词："ZHGXTV" && country="CN" && region="Hunan" && city="changsha"
#            "ZHGXTV" && country="CN" && region="Guangxi Zhuangzu" && port="808"
urls = [
    "https://fofa.info/result?qbase64=InpoZ3h0diI%3D",#zngxtv
]
def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/iptv/live/1000.json?key=txiptv"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)

    return modified_urls


def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=0.5)          ###//////////////////
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None


results = []

for url in urls:
    # 创建一个Chrome WebDriver实例
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    # 使用WebDriver访问网页
    driver.get(url)  # 将网址替换为你要访问的网页地址
    time.sleep(10)
    # 获取网页内容
    page_content = driver.page_source

    # 关闭WebDriver
    driver.quit()

    # 查找所有符合指定格式的网址
    pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"  # 设置匹配的格式，如http://8.8.8.8:8888
    urls_all = re.findall(pattern, page_content)
    # urls = list(set(urls_all))  # 去重得到唯一的URL列表
    urls = set(urls_all)  # 去重得到唯一的URL列表
    x_urls = []
    def is_http_port(ip, port,timeout=2):
    #判断是否为http端口
     try:
        rsp = requests.get(f'http://{ip}:{port}',headers=headers,timeout=timeout)
        if rsp.status_code == 200:
            #状态码等于200则正常
            if 'ZHGXTV' in rsp.text.upper():
                print(f'http://{ip}:{port} 智慧光迅酒店管理系统，正常访问\n')
                valid_data.append(('zhgx',f'{ip}:{port}'))
            elif '/iptv/live/zh_cn.js' in rsp.text.lower():
                print(f'http://{ip}:{port} 智能桌面管理系统，正常访问\n')
                valid_data.append(('znzm',f'{ip}:{port}'))
            else:
                print(f'http://{ip}:{port} 未知系统或者其他WEB？？？')
            return True
        else:
            return False
    except Exception as e:
        return False

    valid_urls = []
    #   多线程获取可用url
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for url in urls:
            url = url.strip()
            modified_urls = modify_urls(url)
            for modified_url in modified_urls:
                futures.append(executor.submit(is_url_accessible, modified_url))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid_urls.append(result)

    for url in valid_urls:
        print(url)
    # 遍历网址列表，获取JSON文件并解析
    for url in valid_urls:
        try:
            # 发送GET请求获取JSON文件，设置超时时间为0.5秒
            ip_start_index = url.find("//") + 2
            ip_dot_start = url.find(".") + 1
            ip_index_second = url.find("/", ip_dot_start)
            base_url = url[:ip_start_index]  # http:// or https://
            ip_address = url[ip_start_index:ip_index_second]
            url_x = f"{base_url}{ip_address}"

            json_url = f"{url}"
            response = requests.get(json_url, timeout=1)                        ####///////////////
            json_data = response.json()

            try:
                # 解析JSON文件，获取name和url字段
                for item in json_data['data']:
                    if isinstance(item, dict):
                        name = item.get('name')
                        urlx = item.get('url')
                        if ',' in urlx:
                            urlx = f"aaaaaaaa"

                        #if 'http' in urlx or 'udp' in urlx or 'rtp' in urlx:
                        if 'http' in urlx:
                          if 'udp' not in urlx:
                            urld = f"{urlx}"
                        else:
                            urld = f"{url_x}{urlx}"


                        if name and urld:
                            name = name.replace("高清电影", "影迷电影")                            
                            name = name.replace("中央", "CCTV")
                            name = name.replace("高清", "")
                            name = name.replace("HD", "")
                            name = name.replace("标清", "")
                            name = name.replace("超高", "")
                            name = name.replace("频道", "")
                            results.append(f"{name},{urld}")
            except:
                continue
        except:
            continue

channels = []

for result in results:
    line = result.strip()
    if result:
        channel_name, channel_url = result.split(',')
        channels.append((channel_name, channel_url))

with open("iptv.txt", 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result + "\n")
        print(result)
print("频道列表文件iptv.txt获取完成！")


#########去重
with open("iptv.txt", 'r', encoding="utf-8") as f:
    lines = f.readlines()
    before = len(lines)
    lines = list(set(lines))
    after = len(lines)
with open('iptv.txt', 'w', encoding='UTF-8') as f:
    for line in lines:          
      f.write(line)
print('处理完成：')
print(f'处理前文件行数：{before}')
print(f'处理后文件行数：{after}')
######
for line in fileinput.input("iptv.txt", inplace=True):  #打开文件，并对其进行关键词原地替换                     ###########
    line = line.replace("CHC电影", "影迷电影")                                                                         ###########                                                      ###########
    print(line, end="")  #设置end=""，避免输出多余的换行符     

import eventlet

eventlet.monkey_patch()

# 线程安全的队列，用于存储下载任务
task_queue = Queue()

# 线程安全的列表，用于存储结果
results = []

channels = []
error_channels = []
# 从iptv.txt文件内提取其他频道进行检测并分组
with open("iptv.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line:
            channel_name, channel_url = line.split(',')
            if 'genre' not in channel_url:
                channels.append((channel_name, channel_url))


# 定义工作线程函数
def worker():
    while True:
        # 从队列中获取一个任务
        channel_name, channel_url = task_queue.get()
        try:
            channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
            lines = requests.get(channel_url).text.strip().split('\n')  # 获取m3u8文件内容
            ts_lists = [line.split('/')[-1] for line in lines if line.startswith('#') == False]  # 获取m3u8文件下视频流后缀
            ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
            ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接
            

            # 获取的视频数据进行5秒钟限制
            with eventlet.Timeout(500, False):  #################////////////////////////////////
                start_time = time.time()
                content = requests.get(ts_url).content
                end_time = time.time()
                response_time = (end_time - start_time) * 1

            if content:
                with open(ts_lists_0, 'ab') as f:
                    f.write(content)  # 写入文件
                file_size = len(content)
                # print(f"文件大小：{file_size} 字节")
                download_speed = file_size / response_time / 1024
                # print(f"下载速度：{download_speed:.3f} kB/s")
                normalized_speed = min(max(download_speed / 1024, 0.001), 100)  # 将速率从kB/s转换为MB/s并限制在1~100之间
                # print(f"标准化后的速率：{normalized_speed:.3f} MB/s")

                # 删除下载的文件
                os.remove(ts_lists_0)
                result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
                results.append(result)
                numberx = (len(results) + len(error_channels)) / len(channels) * 100
                print(
                    f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
        except:
            error_channel = channel_name, channel_url
            error_channels.append(error_channel)
            numberx = (len(results) + len(error_channels)) / len(channels) * 100
            print(
                f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")

        # 标记任务完成
        task_queue.task_done()


# 创建多个工作线程
num_threads = 200
for _ in range(num_threads):
    t = threading.Thread(target=worker, daemon=True)
    # t = threading.Thread(target=worker, args=(event,len(channels)))  # 将工作线程设置为守护线程
    t.start()
    # event.set()

# 添加下载任务到队列
for channel in channels:
    task_queue.put(channel)

# 等待所有任务完成
task_queue.join()


def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字


# 对频道进行排序
results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))
results.sort(key=lambda x: channel_key(x[0]))
result_counter = 100  # 每个频道需要的个数

with open("hn.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('央视频道/自动更新,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' in channel_name or '动作' in channel_name or '家庭' in channel_name or '影迷' in channel_name:
          if '剧场' not in channel_name and '风云' not in channel_name and '教育' not in channel_name and '经典' not in channel_name:  
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    file.write('卫视频道/自动更新,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '湖北卫视' in channel_name or '凤凰卫视' in channel_name or '湖南卫视' in channel_name or '卫视' in channel_name or '江苏卫视' in channel_name or '山东卫视' in channel_name or '安徽卫视' in channel_name or '北京卫视' in channel_name or '广东卫视' in channel_name or '广东珠江' in channel_name or '贵州卫视' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1


    channel_counters = {}
    file.write('省市频道/自动更新,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '湖北' in channel_name or '武汉' in channel_name or '湖南' in channel_name or '南宁' in channel_name or '河北' in channel_name or '广东' in channel_name or '广西' in channel_name or '保定' in channel_name or '石家庄' in channel_name:
          if 'CCTV' not in channel_name and '卫视' not in channel_name:  
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1



    channel_counters = {}
    file.write('港澳频道/随时失效,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '龙祥' in channel_name or '翡翠' in channel_name or '酒店' in channel_name or 'AXN' in channel_name or '东森' in channel_name or '莲花' in channel_name or '天映' in channel_name or '好莱坞' in channel_name or '星河' in channel_name or '私人' in channel_name or '哔哩' in channel_name or '凤凰' in channel_name:
          #if 'CCTV' not in channel_name and '卫视' not in channel_name and 'TV' not in channel_name and '儿' not in channel_name and '文' not in channel_name and 'CHC' not in channel_name and '新' not in channel_name and '山东' not in channel_name and '河北' not in channel_name and '哈哈' not in channel_name and '临沂' not in channel_name and '公共' not in channel_name and 'CETV' not in channel_name and '交通' not in channel_name and '冬' not in channel_name and '梨园' not in channel_name and '民生' not in channel_name and '综合' not in channel_name and '法制' not in channel_name and '齐鲁' not in channel_name and '自办' not in channel_name and '都市' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1    

    channel_counters = {}
    file.write('其他频道/自动更新,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        #if '广' in channel_name or '黑龙江' in channel_name or '南宁' in channel_name:
        if 'CCTV' not in channel_name and '卫视' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1





      
# 合并自定义频道文件内容
file_contents = []
file_paths = ["GAT.txt", "hn.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)



# 写入合并后的文件
with open("iptv_list.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))
for line in fileinput.input("iptv_list.txt", inplace=True):  #打开文件，并对其进行关键词原地替换 
    line = line.replace("AA", "")
    print(line, end="")  #设置end=""，避免输出多余的换行符          
#########原始顺序去重，以避免同一个频道出现在不同的类中
with open('iptv_list.txt', 'r', encoding="utf-8") as file:
 lines = file.readlines()
# 使用列表来存储唯一的行的顺序 
 unique_lines = [] 
 seen_lines = set() 
# 遍历每一行，如果是新的就加入unique_lines 
for line in lines:
 if line not in seen_lines:
  unique_lines.append(line)
  seen_lines.add(line)
# 将唯一的行写入新的文档 
with open('iptv_list.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)
#####################
os.remove("iptv.txt")
os.remove("GAT.txt")
os.remove("hn.txt")
#os.remove("HK.txt")
os.remove("TW.txt")
os.remove("ott移动v4.txt")
print("任务运行完毕")
