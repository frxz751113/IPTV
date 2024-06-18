import os
import re
import time
import datetime
import threading
from queue import Queue
import requests
import eventlet
eventlet.monkey_patch()

# 线程安全的队列，用于存储下载任务
task_queue = Queue()

# 线程安全的列表，用于存储结果
results = []

channels = []
error_channels = []

with open("tv/itv.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line:
            channel_name, channel_url = line.split(',')
                
            renhe_channels = ['电影', '剧场', '电视剧', '相声小品', 'CHC']
            # 检查频道名称是否不包含要排除的频道名称
            if any(excluded in channel_name for excluded in renhe_channels):
                channels.append((channel_name, channel_url))

# 定义工作线程函数
def worker():
    while True:
        # 从队列中获取一个任务
        channel_name, channel_url = task_queue.get()
        try:
            channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
            lines = requests.get(channel_url,timeout=1).text.strip().split('\n')  # 获取m3u8文件内容
            ts_lists = [line.split('/')[-1] for line in lines if line.startswith('#') == False]  # 获取m3u8文件下视频流后缀
            ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
            ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接

            # 多获取的视频数据进行5秒钟限制
            with eventlet.Timeout(5, False):
                start_time = time.time()
                content = requests.get(ts_url,timeout=1).content
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
                #print(f"标准化后的速率：{normalized_speed:.3f} MB/s")

                # 删除下载的文件
                os.remove(ts_lists_0)
                result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
                results.append(result)
                numberx = (len(results) + len(error_channels)) / len(channels) * 100
                print(f"其他  可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
        except:
            error_channel = channel_name, channel_url
            error_channels.append(error_channel)
            numberx = (len(results) + len(error_channels)) / len(channels) * 100
            print(f"其他  可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")

        # 标记任务完成
        task_queue.task_done()


# 创建多个工作线程
num_threads = 10
for _ in range(num_threads):
    t = threading.Thread(target=worker, daemon=True) 
    #t = threading.Thread(target=worker, args=(event,len(channels)))  # 将工作线程设置为守护线程
    t.start()
    #event.set()

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
#results.sort(key=lambda x: channel_key(x[0]))
now_today = datetime.date.today()
# 将结果写入文件

result_counter = 8  # 每个频道需要的个数

# 打开文件，准备写入
with open("tv/qita.txt", 'w', encoding='utf-8') as file:
    # 创建一个字典来存储每个频道的计数
    channel_counters = {}
    # 写入文件的开头部分
    file.write('其他频道,#genre#\n')
    # 遍历结果列表
    for result in results:
        # 解包结果元组
        channel_name, channel_url, speed = result
        # 创建一个列表来存储要排除的频道名称
        excluded_channels = ['CCTV', '卫视', '测试', 'CETV', '教育', '公共']

        # 检查频道名称是否不包含要排除的频道名称
        if not any(excluded in channel_name for excluded in excluded_channels):
            # 获取频道的计数，如果频道不在字典中，就返回 0
            count = channel_counters.get(channel_name, 0)
            if count < result_counter:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = count + 1


    from datetime import datetime, timedelta, timezone
    # 创建一个时区对象表示北京时间
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    now_today = now.strftime("%m月%d日%H时")            
    file.write(f"\n{now_today},#genre#\n\nCCTV1,http://58.210.60.226:9901/tsfile/live/0001_1.m3u8?key=txiptv&playlive=1&authid=0\n")

