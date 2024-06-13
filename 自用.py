import re
import os

with open('iptv_list.txt', 'r', encoding='utf-8') as f:  #打开文件，并对其进行关键词提取                                               ###########
 keywords = ['CCTV', '动作', '家庭', '影迷']  # 需要提取的关键字列表                                                       ###########
 pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字                                      ###########
 #pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制                                                     ###########
 with open('iptv_list.txt', 'r', encoding='utf-8') as file, open('a.txt', 'w', encoding='utf-8') as a:           ###########
    a.write('\n央视,#genre#\n')                                                                        ###########
    for line in file:
     if 'wh7f' not in line and 'ottrrs' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字                                                ###########
          a.write(line)  # 将该行写入输出文件                                                               ###########
                                                                                                           ###########
 
    
with open('iptv_list.txt', 'r', encoding='utf-8') as f:  #打开文件，并对其进行关键词提取                                               ###########
 keywords = ['卫视']  # 需要提取的关键字列表                                                       ###########
 pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字                                      ###########
 #pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制                                                     ###########
 with open('iptv_list.txt', 'r', encoding='utf-8') as file, open('b.txt', 'w', encoding='utf-8') as b:           ###########
    b.write('\n卫视,#genre#\n')                                                                        ###########
    for line in file:
      if 'wh7f' not in line and 'ottrrs' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字                                                ###########
          b.write(line)  # 将该行写入输出文件                                                               ###########
                                                  
    


##############################################################################################################################################################################################################################################

with open('iptv_list.txt', 'r', encoding='utf-8') as f:  #打开文件，并对其进行关键词提取                                               ###########
 keywords = ['湖南', '湖北', '武汉', '广东', '广西', '河北']  # 需要提取的关键字列表                                                       ###########
 pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字                                      ###########
 #pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制                                                     ###########
 with open('iptv_list.txt', 'r', encoding='utf-8') as file, open('c.txt', 'w', encoding='utf-8') as c:           ###########
    c.write('\n省市,#genre#\n')                                                                        ###########
    for line in file:
      if 'wh7f' not in line and 'ottrrs' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字 
          c.write(line)  # 将该行写入输出文件
                                                  
channel_counters = {}
with open('iptv_list.txt', 'r', encoding='utf-8') as f:  #打开文件，并对其进行关键词提取                                               ###########
 keywords = ['龙祥', '翡翠', '酒店', 'AXN', '东森', '天映', '星河', '私人', '哔哩', '凤凰']  # 需要提取的关键字列表                                                       ###########
 pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字                                      ###########
 #pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制                                                     ###########
 with open('iptv_list.txt', 'r', encoding='utf-8') as file, open('d.txt', 'w', encoding='utf-8') as d:           ###########
    d.write('\n港澳,#genre#\n')                                                                        ###########
    for line in file:
      if 'wh7f' not in line and 'ottrrs' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字                                                ###########
          d.write(line)  # 将该行写入输出文件                                                               ###########
                                                  

        


###########################################################################################################################################################################
# 读取要合并的频道文件，并生成临时文件##############################################################################################################
file_contents = []
file_paths = ["a.txt", "b.txt", "c.txt", "d.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)
# 生成合并后的文件
with open("自用.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))


##############################原始顺序去重
# 打开文档并读取所有行 
with open('自用.txt', 'r', encoding="utf-8") as file:
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
with open('自用.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)
##############################



os.remove("a.txt")
os.remove("b.txt")
os.remove("c.txt")
os.remove("d.txt")

print("任务运行完毕，分类频道列表可查看文件夹内.txt文件！")
