import os, sqlite3

import shutil
from bs4 import BeautifulSoup

"""
将抓取的廖雪峰的官方网站(http://www.liaoxuefeng.com/)的教程网页转换为Dash文档
"""


def copy_file(src, doc_name):
    if os.path.exists("dashdoc/" + doc_name):
        shutil.rmtree("dashdoc/" + doc_name)
    shutil.copytree(src, "dashdoc/" + doc_name + "/Contents/Resources/Documents")


def create_xml(doc_name, CFBundleIdentifier, CFBundleName, DocSetPlatformFamily, dashIndexFilePath):
    xml = []
    xml.append(r'<?xml version="1.0" encoding="UTF-8"?>' + '\n')
    xml.append(
        r'<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">' + '\n')
    xml.append(r'<plist version="1.0">' + '\n')
    xml.append(r'<dict>' + '\n')
    xml.append(r'	<key>CFBundleIdentifier</key>' + '\n')
    xml.append(r'	<string>' + CFBundleIdentifier + r'</string>' + '\n')
    xml.append(r'	<key>CFBundleName</key>' + '\n')
    xml.append(r'	<string>' + CFBundleName + r'</string>' + '\n')
    xml.append(r'	<key>DocSetPlatformFamily</key>' + '\n')
    xml.append(r'	<string>' + DocSetPlatformFamily + r'</string>' + '\n')
    xml.append(r'	<key>dashIndexFilePath</key>' + '\n')
    xml.append(r'	<string>' + dashIndexFilePath + r'</string>' + '\n')
    xml.append(r'	<key>isDashDocset</key>' + '\n')
    xml.append(r'	<true/>' + '\n')
    xml.append(r'</dict>' + '\n')
    xml.append(r'</plist>' + '\n')
    xml_str = ''.join(xml)

    file = open("dashdoc/" + doc_name + '/Contents/Info.plist', 'w')
    file.write(xml_str)


def create_db(doc_name, index_html_name):
    conn = sqlite3.connect("dashdoc/" + doc_name + '/Contents/Resources/docSet.dsidx')
    cur = conn.cursor()

    try:
        cur.execute('DROP TABLE searchIndex;')
    except:
        pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    docpath = "dashdoc/" + doc_name + '/Contents/Resources/Documents/wiki/'

    page = open(os.path.join(docpath, index_html_name)).read()
    soup = BeautifulSoup(page, "lxml")

    lis = soup.find("div", {"class": "x-sidebar-left-content"}).findAll("ul")[1].findAll("li")
    for li in lis:
        name = li.get_text().strip()
        path = "wiki/" + li.find("a").attrs["href"].strip()
        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'Keyword', path))
        print('name: %s, path: %s' % (name, path))

    conn.commit()
    conn.close()


copy_file("liaoxuefeng/python", "pythonliaoxuefeng_zh.docset")
create_xml("pythonliaoxuefeng_zh.docset", "python", "PythonLiaoXueFeng_zh", "python",
           "wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000.html")
create_db("pythonliaoxuefeng_zh.docset", "0014316089557264a6b348958f449949df42a6d3a2e542c000.html")

copy_file("liaoxuefeng/git", "gitliaoxuefeng_zh.docset")
create_xml("gitliaoxuefeng_zh.docset", "git", "GitLiaoXueFeng_zh", "git",
           "wiki/0013739516305929606dd18361248578c67b8067c8c017b000.html")
create_db("gitliaoxuefeng_zh.docset", "0013739516305929606dd18361248578c67b8067c8c017b000.html")

copy_file("liaoxuefeng/javascript", "javascriptliaoxuefeng_zh.docset")
create_xml("javascriptliaoxuefeng_zh.docset", "javascript", "JavaScriptLiaoXueFeng_zh", "javascript",
           "wiki/001434446689867b27157e896e74d51a89c25cc8b43bdb3000.html")
create_db("javascriptliaoxuefeng_zh.docset", "001434446689867b27157e896e74d51a89c25cc8b43bdb3000.html")
