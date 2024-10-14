import os
import re
import time

import pyttsx3	# type: ignore
import requests	# type: ignore
import argparse
from bs4 import BeautifulSoup	# type: ignore


_HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.5.715 Yowser/2.5 Safari/537.36',
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'accept-language': 'ru,en;q=0.9',
}
BASE_DIR = os.getcwd()


def get_html(url: str, headers, **params) -> str:
	""" Получить HTML страницы """
	res = requests.get(url, headers=headers, params=params)

	if res.ok:
		return res.text

	raise requests.exceptions.ConnectTimeout


def get_soup(html: str) -> str:
	""" Получить объект парсера HTML """
	soup = BeautifulSoup(html, 'html.parser')

	return soup


def get_text(soup: str) -> str:
	""" Получить текст контента """
	text = ''
	content_block = soup.find('article', class_='tm-article-presenter__content')
	h1 = soup.find('h1', class_='tm-title_h1').text
	text += h1 + '\n\n'
	ps = content_block.find_all('p')
	for p in ps:
		text += p.text + '\n'

	return text


def main(url: str, run_file: bool=True):
	engine = pyttsx3.init()
	html = get_html(url, headers=_HEADERS)
	soup = get_soup(html)
	text_for_synth = get_text(soup)
	reg = re.compile('[^a-zA-Zа-яА-Я1-9. ]')
	h1 = reg.sub('', text_for_synth.split('\n')[0])

	files_dir = os.path.join(BASE_DIR, 'files')
	if not os.path.exists(files_dir):
		os.makedirs(files_dir)

	filename = f'{str(int(time.time()*1000))} {h1}.wav'
	path = os.path.join(files_dir, filename)
	engine.save_to_file(text=text_for_synth, filename=path)
	engine.runAndWait()

	if run_file:
		print(f'{path=}')
		os.system(f'"{path}"')


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-u', '--url', default=None)
	parser.add_argument('-r', '--run', default=True)

	args = parser.parse_args()
	if not args.url:
		args.url = 'https://habr.com/ru/articles/1/'

	main(url=args.url, run_file=args.run)
