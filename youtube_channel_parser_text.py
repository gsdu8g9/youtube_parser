#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

from urllib.request import urlopen
import json
from bs4 import BeautifulSoup
from tkinter import *

def video_parser(i,*params):
	video_id = "http://www.youtube.com/watch?v=" + i.get("data-context-item-id", "")
	title = i.find("a", "yt-uix-tile-link").text
	duration = i.find("span", "video-time").contents[0].text
	views = i.find("ul", "yt-lockup-meta-info").contents[0].text
	#views_num = "".join([i for i in views if i.isdigit()])
	date = i.find("ul", "yt-lockup-meta-info").contents[1].text
	img = i.find("img")
	thumbnail = "http:" + img.get("src", "") if img else ""
	if "usual" in params:
		return "* {0} // {1} // {2} // {3}\n".format(title, duration, views, date)
	elif  "dokuwiki" in params:
		return "  * [[{0}|{1}]]  //длит: {2}//\n".format(video_id, title, duration)
	elif  "dokuwikifull" in params:
		return "  * {{{{{3}?nolink&100|}}}}[[{0}|{1}]]  //длит: {2}//\n".format(video_id, title, duration, thumbnail)

def find_load_more_url(page):
	for button in page.find_all("button"):
		url = button.get("data-uix-load-more-href")
		if url:
			return "http://www.youtube.com" + url

def find_channel_url(page):
	parse_url = page.find("div", class_="yt-user-info").find("a")
	return "http://www.youtube.com" + parse_url.get("href") + "/videos"

def find_channel_name(page):
	return page.find("span", "qualified-channel-title-text").text

def start(URL_CHANNEL, *params):
	html = urlopen(URL_CHANNEL).read()
	page = BeautifulSoup(html)
	
	global channel_name
	channel_name = page.find("span", "qualified-channel-title-text").text
	
	video_divs = page.find_all("div", "yt-lockup-video")

	videos = [video_parser(i, params[0]) for i in video_divs]

	page_url = find_load_more_url(page)

	videos_more_all = []
	while page_url:
		json_data = json.loads(urlopen(page_url).read().decode('utf-8'))
		page_more = BeautifulSoup(json_data.get("content_html", ""))
		video_divs_more = page_more.find_all("div", "yt-lockup-video")
		videos_more = [video_parser(i, params[0]) for i in video_divs_more]
		videos_more_all.extend(videos_more)
		page_url = find_load_more_url(BeautifulSoup(json_data.get("load_more_widget_html", "")))

	videos.extend(videos_more_all)

	return videos

def printer(*params):
	try:
		page_url = ent.get()

		if len(page_url) == 0:
			tex.delete(1.0,END)
			tex.insert(END,"Введите канал пользователя корректно!")
		
		elif "/featured" in page_url:
			page_url = page_url.replace("/featured","/videos")

		elif "/watch?v=" in page_url:
			html = urlopen(page_url).read()
			soup = BeautifulSoup(html)
			parse_url = soup.find("div", class_="yt-user-info").find("a")
			page_url = "http://www.youtube.com" + parse_url.get("href") + "/videos"

		elif "/videos" not in page_url:
			page_url = page_url + "/videos"

		
		if "usual" in params:
			videos = start(page_url, params[0])
		elif  "dokuwikifull" in params:
			videos = start(page_url, params[0])
		elif  "dokuwiki" in params:
			videos = start(page_url, params[0])

		ent.delete(0,END)
		ent.insert(0,page_url)
		tex.delete(1.0,END)
		tex.insert(1.0,"Название канала: {0}".format(channel_name))
		tex.insert(END,"\n\nНа канале {0} видео\n\n".format(len(videos)))
		for video in videos:
			tex.insert(END,video)
	except:
		tex.delete(1.0,END)
		tex.insert(1.0,"Некорректная ссылка")
	
	
root = Tk()
root.title("Парсер youtube-каналов")
root.resizable(width=False, height=True)

lab = Label(root, text="Введите ссылку на канал или видео: ")
lab.grid(row=0, column=0)

ent = Entry(root,width=60)
ent.grid(row=0, column=1, columnspan=3)
ent.insert(0,"http://www.youtube.com/watch?v=gk7X9iytuOM")

lab1 = Label(root, text="Формат вывода: ")
lab1.grid(row=1, column=0)

butt0 = Button(root, text = "Название // длительность", command= lambda: printer("usual"))
butt0.grid(row=1, column=1)

butt1 = Button(root, text = "Список в dokuwiki", command= lambda: printer("dokuwiki"))
butt1.grid(row=1, column=2)

butt2 = Button(root, text = "dokuwiki + preview", command= lambda: printer("dokuwikifull"))
butt2.grid(row=1, column=3)

tex = Text(root, width=115, height=40, wrap=WORD)
scr = Scrollbar(root,command=tex.yview)
tex.configure(yscrollcommand=scr.set)
tex.grid(row=2, column=0, columnspan=4)
scr.grid(row=2, column=4, sticky='nsew')

root.mainloop()
