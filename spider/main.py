#-*- coding:utf-8 -*-
import os
import re
import urllib2
from bs4 import BeautifulSoup

spide_url = "http://www.liaoxuefeng.com/wiki/001434446689867b27157e896e74d51a89c25cc8b43bdb3000"
out_fname = os.path.join(os.getcwd(), "out_txt.txt")

def write2file(fname, text):
    if 0 == len(text):
        print "write file %s error"%fname
    try:
        out_file = open(fname, "w")
        out_file.write(text)
    except IOError, err:
        print "write file %s error: %s"%(fname, err)
    finally:
        if out_file:
            out_file.close()
    print "write file %s success"%fname
def get_content(tag_body):
    tag_div_list = tag_body.find_all("div", id="main")
    tag_div_main = tag_div_list[0]
    tag_content_list = tag_div_main.find_all("div")
    for each in tag_content_list:
        if "class" in each.attrs and "x-wiki-content" in each["class"]:
            tag_content = each
            break
    return str(tag_content)

def main():
    response = urllib2.urlopen(spide_url)
    html_text = response.read()
    
    soup = BeautifulSoup(html_text)
    tag_body = soup.body
    tag_div_list = tag_body.find_all("div", id="main")
    tag_div_main = tag_div_list[0]
    tag_content_list = tag_div_main.find_all("div")
    for each in tag_content_list:
        if "class" in each.attrs and "x-wiki-content" in each["class"]:
            tag_content = each
            break
    out_fname_0 = os.path.splitext(out_fname)[0] + "_first.txt"
    write2file(out_fname_0, str(tag_content))
    
    tag_chapter_list = tag_div_main.find_all("li", id=True, style=re.compile("^margin-left"))
    length = len(tag_chapter_list)
    if 0 == length:
        print "error"
    for num in xrange(length):
        try:
            tag_chapter = tag_chapter_list[num].a
            url_chapter = "http://www.liaoxuefeng.com" + tag_chapter["href"]
            chapter_response = urllib2.urlopen(url_chapter)
            chapter_html_text = chapter_response.read()
            chapter_soup = BeautifulSoup(chapter_html_text)
            fname_key = tag_chapter.string
            fname_key = fname_key.replace("/", "_")
            out_fname_chapter = os.path.splitext(out_fname)[0]+"_"+fname_key+".txt"
            chapter_text = get_content(chapter_soup.body)
            write2file(out_fname_chapter, chapter_text)
        except urllib2.HTTPError, err:
            print err


if __name__ == "__main__":
    main()
    print "success"
