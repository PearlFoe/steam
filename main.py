from steam import *
from config import *

import datetime
import openpyxl
import requests
import time
import json

valid_items = []
valid_data = []
'''
MAX_PRICE = 0
MIN_VOLUME = 0
MIN_PROFIT = 0
'''
def get_valid_items_by_price_filter(session):
	page = 75
	while True:
		flag = False
		items = None

		while True:
			try:
				items = get_item_list(session=session, page_number=page)
				break
			except Exception:
				print('got ban, waiting 3 min')
				time.sleep(BAN_SLEEP_DELAY)

		for item in items:
			if item["sell_price"] <= MAX_PRICE:
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
			time.sleep(SLEEP_DELAY)
			break
		if page >= 90:
			break

		page += 1
		print(f'page {page}\n')
		time.sleep(SLEEP_DELAY)
		
def get_valid_items_by_volume_filter(session):
	for item in valid_items:
		app_id = item['asset_description']['appid']
		name = item['asset_description']['market_hash_name']
		volume = 0
		flag = None
		data = None
	
		while True:
			data = get_item_data(session=session, app_id=app_id, item_name=name)
			if not data:
				if not flag:
					flag = True
				else:
					continue
				print('waiting')
				time.sleep(BAN_SLEEP_DELAY)
			else:
				break

		try:
			volume = int(data['volume'].replace(',',''))
		except:
			valid_items.remove(item)
			time.sleep(SLEEP_DELAY)
			continue

		if volume < MIN_VOLUME:
			valid_items.remove(item)
		time.sleep(SLEEP_DELAY)

def get_valid_items_by_profit_filter(session):
	for item in valid_items:
		app_id = item['asset_description']['appid']
		name = item['asset_description']['market_hash_name']
		histogram = None
		flag = False

		while True:
			histogram = get_item_price_histogram(session=session,app_id=app_id, item_name=name)
			if not histogram:
				if not flag:
					flag = True
				else:
					continue
				print('waiting')
				time.sleep(BAN_SLEEP_DELAY)
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
			biggest_counter = 0
			for counter, i in enumerate(histogram['buy_order_graph']):
				if int(i[1]) > biggest_counter:
					biggest_counter = int(i[1])
					if counter != 0: 
						buy_price = float(histogram['buy_order_graph'][counter - 1][0])

				if counter + 1 >= DEPTH:
					break

			biggest_counter = 0
			for counter, i in enumerate(histogram['sell_order_graph']):
				if int(i[1]) > biggest_counter:
					biggest_counter = int(i[1])
					if counter < len(histogram['sell_order_graph']): 
						sell_price = float(histogram['sell_order_graph'][counter + 1][0])

				if counter + 1 >= DEPTH:
					break

		print(name, buy_price, sell_price)

		percent = ((sell_price - sell_price * 0.13 - buy_price)/sell_price) * 100

		if percent >= MIN_PROFIT:
			#valid_items.remove(item)
			time.sleep(SLEEP_DELAY)
			valid_data.append([name, sell_price, buy_price, percent])
			continue
		time.sleep(SLEEP_DELAY)


def get_settings():
	with open('config.json', 'r') as f:
		data = json.load(f)
		global MAX_PRICE
		MAX_PRICE = data['max_price']
		global MIN_VOLUME
		MIN_VOLUME = data['min_volume']
		global MIN_PROFIT
		MIN_PROFIT = data['min_profit']


def main():
	session = requests.Session()
	session.get('https://steamcommunity.com/market/')
	session.headers.update(headers)
	session.cookies.update(cookies)

	#get_settings()

	print('Started')
	get_valid_items_by_price_filter(session=session)
	print('getting volume', str(len(valid_items)))
	get_valid_items_by_volume_filter(session=session)
	print('gettint profit', str(len(valid_items)))
	get_valid_items_by_profit_filter(session=session)
	print(f'stored items count {len(valid_data)}')

	wb = openpyxl.Workbook()
	sheet = wb['Sheet']

	head = ['Название','Цена продажи','Цена покупки','Профит(%)']
	sheet.append(head)
	
	for counter, item in enumerate(valid_data):
		sheet.append(item)

	wb.save('data.xlsx')


if __name__ == "__main__":
	main()



