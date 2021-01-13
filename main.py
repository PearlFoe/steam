from tkinter import *

from GUI import Menu
from steam import *
import config

import datetime
import openpyxl
import requests
import time
import json

valid_items = []
valid_data = []

MAX_PRICE = 0
MIN_VOLUME = 0
MIN_PROFIT = 0
ORDERS_DIFFERENCE_PERCENT = 0
SLEEP_DELAY = 0
BAN_SLEEP_DELAY = 0

def get_valid_items_by_price_filter(session, app_id):
	'''
	Функция для сбора товаров со страниц сайта по API.
	'''
	page = 0
	while True:
		flag = False
		items = None

		while True:
			try:
				items = get_item_list(session=session, page_number=page, app_id=app_id)
				break
			except Exception:
				print('got ban, waiting 3 min')
				time.sleep(BAN_SLEEP_DELAY.get())

		for counter, item in enumerate(items):
			if item["sell_price"] <= MAX_PRICE.get():
				flag = True
				if item['asset_description']['tradable'] == 1:# and item['asset_description']['marketable'] == 1:
					try:
						if item['asset_description']['marketable'] == 1 and item not in valid_items:
							print(item['asset_description']['market_hash_name'], item["sell_price_text"])

							valid_items.append(item)
					except Exception:
						pass
				elif counter == 0 and page == 0 and item not in valid_items:
					valid_items.append(item)

		#print(items[0]['name'])
		if not flag:
			time.sleep(3)
			break

		page += 1
		print(f'page {page}\n')
		time.sleep(3)

def get_valid_items_by_volume_filter(session, app_id, item_name):
	'''
		Функция для проверки количества 
		сдедлок по конкретному товару.
	'''
	volume = 0
	data = None
	volume_flag = False

	while True:
		try:
			data = get_item_data(session=session, app_id=app_id, item_name=item_name)
		except Exception:
			if not volume_flag:
				volume_flag = True
			else:
				return False
			print('waiting')
			time.sleep(BAN_SLEEP_DELAY.get())
		else:
			break

	try:
		volume = int(data['volume'].replace(',',''))
	except:
		return False

	if volume < MIN_VOLUME.get():
		return False

	return volume

def get_minimal_item_data(session):
	for item in valid_items:
		app_id = item['asset_description']['appid']
		hash_name = item['hash_name']
		name = item['name']
		histogram = None
		histogram_flag = False
		data = None
		sell_order_count = None
		buy_order_count = None
		percent = None

		try:
			data = get_item_data(session=session, app_id=app_id, item_name=hash_name)
			time.sleep(SLEEP_DELAY.get())
		except Exception:
			valid_items.remove(item)
			time.sleep(SLEEP_DELAY.get())
			continue

		if not data:
			valid_items.remove(item)
			continue
		elif not data['success']:
			valid_items.remove(item)
			continue

		try:
			volume = int(data['volume'].replace(',',''))
			min_price = data['lowest_price']
			median_price = data['median_price']

			if volume < MIN_VOLUME.get():
				valid_items.remove(item)
				continue
		except Exception:
			continue
		
		while True:
			try:
				histogram = get_item_price_histogram(session=session,app_id=app_id, item_name=hash_name, sleep_delay=SLEEP_DELAY.get())
			except Exception:
				if not histogram_flag:
					histogram_flag = True
				else:
					break
				print('waiting')
				time.sleep(BAN_SLEEP_DELAY.get())
			else:
				break

		try:
			sell_order_count = int(histogram['sell_order_count'].replace(',',''))
			buy_order_count = int(histogram['buy_order_count'].replace(',',''))
			percent = (buy_order_count * 100 / sell_order_count) - 100 
		except Exception:
			continue

		if percent > ORDERS_DIFFERENCE_PERCENT.get():
			print(hash_name, volume, min_price, median_price)
			time.sleep(SLEEP_DELAY.get())
			valid_data.append([name, f'https://steamcommunity.com/market/listings/{app_id}/{hash_name}', volume, min_price, median_price])
		time.sleep(SLEEP_DELAY.get())

def get_settings():
	'''
		Функция для получения параметров
		поиска из .json файла.
	'''
	with open('config.json', 'r') as f:
		data = json.load(f)
		global MAX_PRICE
		MAX_PRICE = data['MAX_PRICE']
		global MIN_VOLUME
		MIN_VOLUME = data['MIN_VOLUME']
		global MIN_PROFIT
		MIN_PROFIT = data['MIN_PROFIT']

def remove_dublicates_in_valid_data():
	'''
		Функция для получения удаления 
		дубликатов в списке товаров перед
		сохранением их в файл.
	'''
	global valid_data
	lst = [i[0] for i in valid_data]
	for i in valid_data:
		if lst.count(i[0]) > 1:
			valid_data.remove(i)

def get_games_list(file_name):
	with open(file_name, 'r') as f:
		data = json.load(f)

	return data

def main():
	window = Tk()
	window.title("Steam")
	window.geometry('720x350')

	menu = Menu(window)
	list_box_frame = Frame(window)
	list_box = Menu(list_box_frame)

	games = get_games_list('games.json')

	##################################### GUI #############################################
	menu.add_text(text='Выберите игру: ', col=0, row=0, padx=0, pady=0, sticky='nw')
	GAME = list_box.add_list_box(items=games.keys(), side='top')

	list_box_frame.grid(column=0, row=1)

	global MAX_PRICE
	menu.add_text(text='Введите максимальную цену: ', col=1, row=0, padx=0, pady=0, sticky='ne')
	MAX_PRICE = menu.add_entry_window(col=2, row=0)
	
	global MIN_VOLUME
	menu.add_text(text='Введите минимальное\nколичество сделок: ', col=1, row=1, padx=0, pady=0, sticky='nw')
	MIN_VOLUME = menu.add_entry_window(col=2, row=1)

	global ORDERS_DIFFERENCE_PERCENT
	menu.add_text(text='Введите процент: ', col=3, row=0, padx=0, pady=0, sticky='nw')
	ORDERS_DIFFERENCE_PERCENT = menu.add_entry_window(col=4, row=0)

	######################################################################################

	global SLEEP_DELAY
	menu.add_text(text='Введите задержку\nмежду запросами: ', col=1, row=2, padx=0, pady=0, sticky='nw')
	SLEEP_DELAY = menu.add_entry_window(col=2, row=2)

	global BAN_SLEEP_DELAY
	menu.add_text(text='Введите задержку при\nполучении бана: ', col=3, row=2, padx=0, pady=0, sticky='nw')
	BAN_SLEEP_DELAY = menu.add_entry_window(col=4, row=2)

	menu.add_btn(text='Начать', color='green', col=4, row=3)

	window.mainloop()

	##################################### Scrapping ######################################
	
	session = requests.Session()
	session.get('https://steamcommunity.com/market/')
	session.headers.update(config.headers)
	session.cookies.update(config.cookies)

	print('Started')
	try:
		get_valid_items_by_price_filter(session=session, app_id=games[GAME.get()].split('appid=')[-1])
	except Exception:
		print("Error: Game wasn't choosed.")

	print('Scrapped items count:', str(len(valid_items)))

	get_minimal_item_data(session=session)

	################### saving scrapped data ###################

	wb = openpyxl.Workbook()
	sheet = wb['Sheet']

	head = ['Название', 'Ссылка', 'Объем торгов', 'Минимальная цена', 'Медианная цена']
	sheet.append(head)

	remove_dublicates_in_valid_data()
	print(f'Stored items count: {len(valid_data)}')

	for counter, item in enumerate(valid_data):
		sheet.append(item)

	wb.save('data.xlsx')

if __name__ == '__main__':
	main()
