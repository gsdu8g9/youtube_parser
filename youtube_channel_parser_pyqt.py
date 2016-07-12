#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QTextEdit, QGridLayout
from PyQt5.QtGui import QIcon
from urllib.request import urlopen
import json
from bs4 import BeautifulSoup


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
	elif  "browser" in params:
		#~ data = urllib.request.urlopen(thumbnail).read()
		#~ image = QImage()
		#~ image.loadFromData(data)
		#return "<img src='video.png'> - {0} //длит: {1}//\n".format(title, duration)
		return "<img src=http://i50.tinypic.com/34g8vo5.jpg> - {0} //длит: {1}//\n".format(title, duration)


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
		page_url = ent.text()
	
		if "/featured" in page_url:
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
		elif  "browser" in params:
			videos = start(page_url, params[0])
	
		#ent.clear()
		ent.setText(page_url)
		tex.clear()
		tex.setText("Название канала: {0}".format(channel_name))
		tex.append("\nНа канале {0} видео:\n".format(len(videos)))
		for video in videos:
			tex.append(video)

	except:
		tex.clear()
		tex.setText("""The truth is out there
						Try this again""")


app = QApplication([])

window = QWidget()
window.setGeometry(500, 150, 1000, 800)
window.setWindowTitle('Парсер каналов youtube.com')
#window.setWindowIcon(QIcon('youtube.png'))
#window.frameGeometry().moveCenter(QDesktopWidget().availableGeometry().center())
window.show()

ent = QLineEdit()
ent.setStyleSheet("background-color: rgb(220, 220, 220); color: red")
ent.setText("http://www.youtube.com/watch?v=gk7X9iytuOM")
#ent.setPlaceholderText("http://www.youtube.com/watch?v=gk7X9iytuOM")

button1 = QPushButton(QIcon('youtube.png'), "Название//длительность")
button1.setToolTip("Вывод в формате: <b>Название</b> // <b>Длительность</b> // <b>Кол-во просмотров</b> // <b>Дата публикации</b>")
button1.setStatusTip('Exit application')
button1.clicked.connect(lambda: printer('usual'))

button2 = QPushButton(QIcon('dokuwiki.png'), "Список dokuwiki")
button2.setToolTip("Вывод в формате ненумерованного списка для <b>dokuwiki</b>")
button2.clicked.connect(lambda: printer('dokuwiki'))

button3 = QPushButton(QIcon('preview.png'),"dokuwiki + preview")
button3.setToolTip("Вывод в формате ненумерованного списка для <b>dokuwiki с превью</b>")
button3.clicked.connect(lambda: printer('dokuwikifull'))

button4 = QPushButton(QIcon('eye.png'),"browser mode")
button4.clicked.connect(lambda: printer('browser'))

tex = QTextEdit()

grid = QGridLayout()
grid.setVerticalSpacing(5)
window.setLayout(grid)

grid.addWidget(ent, 1, 0, 1, 4)
grid.addWidget(button1, 2, 0)
grid.addWidget(button2, 2, 1)
grid.addWidget(button3, 2, 2)
grid.addWidget(button4, 2, 3)
grid.addWidget(tex, 3, 0, 3, 4)

sys.exit(app.exec_())  

