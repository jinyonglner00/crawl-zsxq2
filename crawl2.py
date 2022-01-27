import random
import re
import time

import requests
import json
import os
import pdfkit
from bs4 import BeautifulSoup
from urllib.parse import quote

from requests import options

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
<h1>{title}</h1>
<p>{text}</p>
</body>
</html>
"""
htmls = []
num = 0
def get_data(urls):

    global htmls, num
        
    headers = {
        'Authorization': '73C701DF-E5B7-D3E2-BB10-253450D637F3_471F15AD92F2CB0B',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
    }
    
    url=urls

    for it in range(1000):
            rsp = requests.get(url, headers=headers)
            time.sleep(random.randint(8, 15))
            with open('test.json', 'w', encoding='utf-8') as f:        # 将返回数据写入 test.json 方便查看
                f.write(json.dumps(rsp.json(), indent=2, ensure_ascii=False))
            try:
                with open('test.json', encoding='utf-8-sig',errors='ignore') as f:
                    word=f.read()
                    if json.loads(word).get('resp_data') is not None:
                        topics=json.loads(word).get('resp_data').get('topics')
                    else:
                        continue
                    if topics==None:continue
                    for topic in topics:
                        print(topic)
                        content = topic.get('question', topic.get('talk', topic.get('task', topic.get('solution'))))
                        # print(content)
                        text = content.get('text', '')
                        text = re.sub(r'<[^>]*>', '', text).strip()
                        text = text.replace('\n', '<br>')
                        title = str(num) + text[:9]
                        num += 1
                        time.sleep(random.randint(2, 8))

                        if content.get('images'):
                            soup = BeautifulSoup(html_template, 'html.parser')
                            for img in content.get('images'):
                                url = img.get('large').get('url')
                                img_tag = soup.new_tag('img', src=url)
                                soup.body.append(img_tag)
                                html_img = str(soup)
                                html = html_img.format(title=title, text=text)
                        else:
                            html = html_template.format(title=title, text=text)

                        if topic.get('question'):
                            answer = topic.get('answer').get('text', "")
                            soup = BeautifulSoup(html, 'html.parser')
                            answer_tag = soup.new_tag('p')
                            answer_tag.string = answer
                            soup.body.append(answer_tag)
                            html_answer = str(soup)
                            html = html_answer.format(title=title, text=text)

                        print(topic.get('show_comments'))
                        if topic.get('show_comments'):
                            soup = BeautifulSoup(html, 'html.parser')
                            for owner in topic.get('show_comments'):
                                owner_tag = soup.new_tag('p')
                                owner_tag.string=owner.get('owner').get('name')+":"+owner.get('text')
                                print(owner.get('owner').get('name')+":"+owner.get('text'))
                                soup.body.append(owner_tag)
                                html_img = str(soup)
                                html = html_img.format(title=title, text=text)

                        htmls.append(html)
            except MemoryError as e:
                print(e)
            next_page = rsp.json().get('resp_data').get('topics')
            if next_page:
                create_time = next_page[-1].get('create_time')
                if create_time[20:23] == "000":
                    end_time = create_time[:20]+"999"+create_time[23:]
                else :
                    res = int(create_time[20:23])-1
                    end_time = create_time[:20]+str(res).zfill(3)+create_time[23:] # zfill 函数补足结果前面的零，始终为3位数
                end_time = quote(end_time)
                if len(end_time) == 33:
                    end_time = end_time[:24] + '0' + end_time[24:]
                next_url = start_url + '&end_time=' + end_time
                print(next_url)
                url=next_url
            else:
                break
    return htmls

def make_pdf(htmls):
    html_files = []
    for index, html in enumerate(htmls):
        file = str(index) + ".html"
        html_files.append(file)
        with open(file, "w", encoding="utf-8") as f:
            f.write(html)

    options = {
        "user-style-sheet": "test.css",
        "page-size": "Letter",
        "margin-top": "0.75in",
        "margin-right": "0.75in",
        "margin-bottom": "0.75in",
        "margin-left": "0.75in",
        "encoding": "UTF-8",
        "custom-header": [("Accept-Encoding", "gzip")],
        "cookie": [
            ("cookie-name1", "cookie-value1"), ("cookie-name2", "cookie-value2")
        ],
        "outline-depth": 10,
    }
    try:
        pdfkit.from_file(html_files, "电子书.pdf", options=options)
    except Exception as e:
        pass
        print('错误')

    # for file in html_files:
    #     os.remove(file)

    print("已制作电子书在当前目录！")

if __name__ == '__main__':
    start_url = 'https://api.zsxq.com/v2/groups/48844244452158/topics?scope=all&count=20'

    make_pdf(get_data(start_url))


