from urllib.request import urlopen, urlretrieve
from bs4 import BeautifulSoup
import os
import re

"""
使用爬虫抓取廖雪峰的官方网站(http://www.liaoxuefeng.com/)的教程
"""


class Html:
    """
    html类
    """

    def __init__(self, name, url):
        """
        :param name: 左边index的名字
        :param url: url路径
        """
        self.name = name
        self.url = url


def get_html(url_path):
    """
    获取网页BeautifulSoup对象
    :param url_path: wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000
    :return:BeautifulSoup对象
    """
    global base_url
    html = urlopen(base_url + "/" + url_path)
    bs_obj = BeautifulSoup(html, "lxml")
    return bs_obj


def get_all_index(bs_obj):
    """
    获取左边index的所有链接
    :param bs_obj:BeautifulSoup对象
    :return:左边index的所有链接集合
    """
    html_list = []
    lis = bs_obj.find("div", {"class": "x-sidebar-left-content"}).findAll("ul")[1].findAll("li")
    for li in lis:
        html_list.append(Html(li.get_text().strip(), li.find("a").attrs["href"][1:]))
    return html_list


def download_css(download_directory, bs_obj):
    """
    下载页面所有的css文件
    :param download_directory: 下载文件夹
    :param bs_obj: BeautifulSoup对象
    """
    global source_link
    links = bs_obj.findAll("link", {"rel": "stylesheet"})
    for link in links:
        if link["href"] is not None:
            href = link["href"]
            href = href[1:]
            if href not in source_link:
                source_link.add(href)
                file_dir = os.path.dirname(download_directory + "/" + href)
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                urlretrieve(base_url + "/" + href, download_directory + "/" + href)


def download_page_img(download_directory, bs_obj):
    """
    下载页面所有的图片
    :param download_directory: 下载文件夹
    :param bs_obj:BeautifulSoup对象
    """
    global source_link
    imgs = bs_obj.findAll("img", src=re.compile("^/+.*$"))
    for img in imgs:
        if img["src"] is not None:
            src = img["src"]
            src = src[1:]
            if src not in source_link:
                source_link.add(src)
                file_dir = os.path.dirname(download_directory + "/" + src)
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                urlretrieve(base_url + "/" + src, download_directory + "/" + src + ".png")


def download_page(download_directory, url_path, bs_obj, html_list):
    """
    替换删除网页内容并保存到本地
    :param download_directory: 下载文件夹
    :param url_path:
           网页路径
           wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000
           wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001431608990315a01b575e2ab041168ff0df194698afac000
    :param bs_obj:BeautifulSoup对象
    :param html_list:左边index的所有链接集合
    """

    # 删除javascript
    scripts = bs_obj.findAll("script")
    for script in scripts:
        script.decompose()

    # 删除header
    header = bs_obj.find("div", {"id": "header"})
    header.decompose()
    x_placeholder_50 = bs_obj.find("div", {"class": "x-placeholder-50"})
    x_placeholder_50.decompose()
    x_placeholder = bs_obj.find("div", {"class": "x-placeholder"})
    x_placeholder.decompose()

    # 删除footer
    footer = bs_obj.find("div", {"id": "footer"})
    footer.decompose()

    # 删除promos
    promos = bs_obj.find("div", {"id": "the-promos"})
    promos.decompose()

    # 删除广告
    ads = bs_obj.findAll("ins", {"class": "adsbygoogle"})
    for ad in ads:
        ad.decompose()

    # 删除评论
    comment = bs_obj.find("ul", {"id": "x-comment-list"})
    h3_comment = comment.find_previous_sibling()
    x_anchor = h3_comment.find_previous_sibling()
    hr_above_x_anchor = x_anchor.find_previous_sibling()

    h3_send_comment = comment.find_next()
    x_display_if_not_signin = h3_send_comment.find_next()
    x_comment_area = x_display_if_not_signin.find_next()

    h3_comment.decompose()
    comment.decompose()
    x_anchor.decompose()
    hr_above_x_anchor.decompose()
    h3_send_comment.decompose()
    x_display_if_not_signin.decompose()
    x_comment_area.decompose()

    # 删除wiki-info
    wiki_info = bs_obj.find("div", {"class": "x-wiki-info"})
    wiki_info.decompose()

    # 替换css链接路径
    csss = bs_obj.findAll("link", {"rel": "stylesheet"})
    for css in csss:
        if css["href"] is not None:
            if url_path == html_list[0].url:
                css["href"] = ".." + css["href"]
            else:
                css["href"] = "../.." + css["href"]

    # 替换img链接路径
    imgs = bs_obj.findAll("img", src=re.compile("^/+.*$"))
    for img in imgs:
        if img["src"] is not None:
            if url_path == html_list[0].url:
                img["src"] = ".." + img["src"] + ".png"
            else:
                img["src"] = "../.." + img["src"] + ".png"

    # 替换index中的url路径
    urls = bs_obj.findAll("a", href=True)
    for url in urls:
        if url["href"] is not None and len(url["href"]) > 1:
            href_url = url["href"][1:]
            if href_url == html_list[0].url:
                if url_path == html_list[0].url:
                    url["href"] = os.path.basename(href_url) + ".html"
                else:
                    url["href"] = "../" + os.path.basename(href_url) + ".html"
            else:
                for html in html_list:
                    if href_url == html.url:
                        if url_path == html_list[0].url:
                            url["href"] = os.path.basename(url_path) + "/" + os.path.basename(href_url) + ".html"
                        else:
                            url["href"] = os.path.basename(href_url) + ".html"

    # 保存网页到本地
    file_dir = os.path.dirname(download_directory + "/" + url_path)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    file_write = open(download_directory + "/" + url_path + ".html", mode="w", encoding="utf-8")
    file_write.write(str(bs_obj))
    file_write.close()


def download(download_directory, source_url_path):
    bs_obj_out = get_html(source_url_path)
    html_list_out = get_all_index(bs_obj_out)

    for html_out in html_list_out:
        print(html_out.name + " " + html_out.url)
        bs_obj_new_out = get_html(html_out.url)
        download_css(download_directory, bs_obj_new_out)
        download_page_img(download_directory, bs_obj_new_out)
        download_page(download_directory, html_out.url, bs_obj_new_out, html_list_out)


base_url = "http://www.liaoxuefeng.com"

directory_url_dict = {
    "liaoxuefeng/python": "wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000",
    "liaoxuefeng/javascript": "wiki/001434446689867b27157e896e74d51a89c25cc8b43bdb3000",
    "liaoxuefeng/git": "wiki/0013739516305929606dd18361248578c67b8067c8c017b000"
}

# 网页中引用的css与image资源路径
source_link = set()

for d in directory_url_dict:
    source_link.clear()
    download(d, directory_url_dict[d])
