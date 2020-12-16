from datetime import datetime
import json
import os
import re
import csv

from lxml import etree
import requests


BASE_URL = 'https://s.weibo.com'
TXT_DIR = './txt'


def getHTML(url, needPretty=False):
    ''' 获取网页 HTML 返回字符串

    Args:
        url: str, 网页网址
        needPretty: bool, 是否需要美化(开发或测试时可用)
    Returns:
        HTML 字符串
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    return response.text


def save(filename, content, time_now):
    ''' 写文件

    Args:
        filename: str, 文件路径
        content: str/dict, 需要写入的内容
    Returns:
        None
    '''
    
    filename_txt = os.path.join(TXT_DIR, filename + '.txt')

    with open(filename_txt, 'w', encoding = 'UTF-8') as wf:
        for text in content:
            wf.write(str(text) +','+ str(content[text]['hot']) +','+ str(time_now) + '\n')


# 使用 xpath 解析 HTML
def parseHTMLByXPath(content):
    ''' 使用 xpath 解析 HTML, 提取榜单信息

    Args:
        content: str, 待解析的 HTML 字符串
    Returns:
        榜单信息的字典 字典
    '''
    html = etree.HTML(content)

    titles = html.xpath('//tr[position()>1]/td[@class="td-02"]/a[not(contains(@href, "javascript:void(0);"))]/text()')
    hrefs = html.xpath('//tr[position()>1]/td[@class="td-02"]/a[not(contains(@href, "javascript:void(0);"))]/@href')
    hots = html.xpath('//tr[position()>1]/td[@class="td-02"]/a[not(contains(@href, "javascript:void(0);"))]/../span/text()')
    titles = [title.strip() for title in titles]
    hrefs = [BASE_URL + href.strip() for href in hrefs]
    hots = [int(hot.strip()) for hot in hots]

    correntRank = {}
    for i, title in enumerate(titles):
        correntRank[title] = {'href': hrefs[i], 'hot': hots[i]}

    return correntRank


# 更新本日榜单
def updateJSON(correntRank):
    ''' 更新当天对应小时的 csv 文件

    Args:
        correntRank: dict, 此时榜单信息
    Returns:
        排序后的榜单信息字典（小时计）
    '''
    time_now = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    # 文件不存在则创建
    #if not os.path.exists(filename):
    #    os.mknod(filename)

    nowRank = {}
    for k, v in correntRank.items():
        nowRank[k] = v

    # 将榜单按 hot 值排序
    rank = {k: v for k, v in sorted(nowRank.items(), key=lambda item: item[1]['hot'], reverse=True)}

    # 更新当天榜单 csv 文件
    save(filename, rank, time_now)
    return rank



def main():
    url = '/top/summary?cate=realtimehot'
    content = getHTML(BASE_URL + url)
    correntRank = parseHTMLByXPath(content)
    res = updateJSON(correntRank)


if __name__ == '__main__':
    main()
