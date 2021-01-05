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
PARAM = 0
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

		for item in items:
			if item["sell_price"] <= MAX_PRICE.get():
				flag = True
				if item['asset_description']['tradable'] == 1:# and item['asset_description']['marketable'] == 1:
					try:
						if item['asset_description']['marketable'] == 1:
							print(item['asset_description']['market_hash_name'], item["sell_price_text"])

							valid_items.append(item)
					except Exception:
						pass

		#print(items[0]['name'])
		if not flag:
			time.sleep(3)
			break
		
		if page >= 170:
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
		data = get_item_data(session=session, app_id=app_id, item_name=item_name)
		if not data:
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

def get_valid_items_by_profit_filter(session):
	'''
		Функция для подсчета прибыли от
		покупки/продажи товара.
		На данном этапе также проверятеся
		количество сделок по конкретному товару.
	'''
	for item in valid_items:
		app_id = item['asset_description']['appid']
		hash_name = item['hash_name']
		name = item['name']
		histogram = None
		histogram_flag = False

		volume = get_valid_items_by_volume_filter(session=session, app_id=app_id, item_name=hash_name)
		time.sleep(SLEEP_DELAY.get())
		if not volume:
			valid_items.remove(item)
			continue

		while True:
			histogram = get_item_price_histogram(session=session,app_id=app_id, item_name=hash_name)
			if not histogram:
				if not histogram_flag:
					histogram_flag = True
				else:
					break
				print('waiting')
				time.sleep(BAN_SLEEP_DELAY.get())
			else:
				break

		sell_price = None
		buy_price = None
		try:
			buy_price = int(histogram['highest_buy_order'])
			sell_price = int(histogram['lowest_sell_order'])
		except Exception:
			continue
		else:
			if len(histogram['buy_order_graph']) <= len(histogram['sell_order_graph']):
				depth = len(histogram['buy_order_graph'])
			else:
				depth = len(histogram['sell_order_graph'])

			stored_prices = dict()

			biggest_buy_counter = 0
			sum_buy_count = 0
			
			for counter, i in enumerate(histogram['buy_order_graph']):
				sum_buy_count += int(i[1])
				if int(i[1]) > biggest_buy_counter: 
					biggest_buy_counter = int(i[1])
					if counter != 0:
						buy_price = float(histogram['buy_order_graph'][counter - 1][0])
						
						biggest_sell_counter = 0
						sum_sell_count = 0

						for counter, i in enumerate(histogram['sell_order_graph']):
							sum_sell_count += int(i[1])
							if int(i[1]) > biggest_sell_counter: 
								biggest_sell_counter = int(i[1])
								if counter < len(histogram['sell_order_graph']) - 1:
									if int(histogram['sell_order_graph'][counter + 1][1]) > int(histogram['sell_order_graph'][counter][1]):
										sell_price = float(histogram['sell_order_graph'][counter - 1][0])
										if sum_sell_count + sum_buy_count < volume * PARAM.get():
											percent = ((sell_price - sell_price * 0.13 - buy_price)/sell_price) * 100
											stored_prices[percent] = {'buy_price':buy_price, 'sell_price':sell_price}

									else:
										sell_price = float(histogram['sell_order_graph'][counter + 1][0])
										if sum_sell_count + sum_buy_count < volume * PARAM.get():
											percent = ((sell_price - sell_price * 0.13 - buy_price)/sell_price) * 100
											stored_prices[percent] = {'buy_price':buy_price, 'sell_price':sell_price}
			max_precent = 0
			try:
				max_precent = max(stored_prices)
			except:
				continue
				
			print(hash_name, stored_prices[max_precent]['buy_price'], stored_prices[max_precent]['sell_price'], max_precent)
			if max_precent >= MIN_PROFIT.get():
				#valid_items.remove(item)
				time.sleep(SLEEP_DELAY.get())
				valid_data.append([name, f'https://https://steamcommunity.com/market/listings/{app_id}/{hash_name}', stored_prices[max_precent]['sell_price'], stored_prices[max_precent]['buy_price'], max_precent])
				#print(hash_name, buy_price, sell_price, time.time() - start_time)
				continue
			time.sleep(SLEEP_DELAY.get())

def get_minimal_item_data(session):
	'''
		Функция для сбора минимального объема данных.
		Не делает дополнительные запросы для получения 
		спика цен и не считает profit.
	'''
	for item in valid_items:
		app_id = item['asset_description']['appid']
		hash_name = item['hash_name']
		name = item['name']

		data = get_item_data(session=session, app_id=app_id, item_name=hash_name)
		time.sleep(SLEEP_DELAY.get())
		if not data:
			valid_items.remove(item)
			continue
		elif not data['success']:
			valid_items.remove(item)
			continue

		volume = int(data['volume'].replace(',',''))
		min_price = data['lowest_price']
		median_price = data['median_price']
		if volume < MIN_VOLUME.get():
			valid_items.remove(item)
			continue
			
		print(hash_name, volume, min_price, median_price)
		time.sleep(SLEEP_DELAY.get())
		valid_data.append([name, f'https://https://steamcommunity.com/market/listings/{app_id}/{hash_name}', volume, min_price, median_price])

def get_settings():
	'''
		Функция для получения параметров
		поиска из .json файлка.
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

	global MIN_PROFIT
	menu.add_text(text='Введите минимальный\nпроцент прибыли: ', col=3, row=0, padx=0, pady=0, sticky='nw')
	MIN_PROFIT = menu.add_entry_window(col=4, row=0)

	global PARAM
	menu.add_text(text='Введите коэффициент: ', col=3, row=1, padx=0, pady=0, sticky='nw')
	PARAM = menu.add_entry_window(col=4, row=1)

	######################################################################################

	global SLEEP_DELAY
	menu.add_text(text='Введите задержку\nмежду запросами: ', col=1, row=2, padx=0, pady=0, sticky='nw')
	SLEEP_DELAY = menu.add_entry_window(col=2, row=2)

	global BAN_SLEEP_DELAY
	menu.add_text(text='Введите задержку при\nполучении бана: ', col=3, row=2, padx=0, pady=0, sticky='nw')
	BAN_SLEEP_DELAY = menu.add_entry_window(col=4, row=2)

	######################################################################################

	GET_MIN_DATA_FLAG = menu.add_check_btn(text='Собирать минимальный\nобъем данных', col=3, row=3)
	menu.add_btn(text='Начать', color='green', col=4, row=3)

	window.mainloop()

	##################################### Scrapping ######################################

	session = requests.Session()
	session.get('https://steamcommunity.com/market/')
	session.headers.update(config.headers)
	session.cookies.update(config.cookies)

	print('Started')
	get_valid_items_by_price_filter(session=session, app_id=games[GAME.get()].split('appid=')[-1])
	print('Scrapped items count:', str(len(valid_items)))

	if GET_MIN_DATA_FLAG.get():
		get_minimal_item_data(session=session)
	else:
		get_valid_items_by_profit_filter(session=session)

	################### saving scrapped data ###################

	wb = openpyxl.Workbook()
	sheet = wb['Sheet']

	if GET_MIN_DATA_FLAG.get():
		head = ['Название', 'Ссылка', 'Объем торгов', 'Минимальная цена', 'Медианная цена']
	else:
		head = ['Название', 'Ссылка', 'Цена продажи', 'Цена покупки', 'Прибыль(%)']

	sheet.append(head)

	remove_dublicates_in_valid_data()
	print(f'Stored items count: {len(valid_data)}')

	for counter, item in enumerate(valid_data):
		sheet.append(item)

	wb.save('data.xlsx')

if __name__ == "__main__":
	main()