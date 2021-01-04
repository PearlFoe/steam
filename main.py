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
	page = 100
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
			time.sleep(3)
			break
		
		if page >= 170:
			break
		
		page += 1
		print(f'page {page}\n')
		time.sleep(3)
'''	
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
'''
def get_valid_items_by_volume_filter(session, app_id, item_name):
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
			time.sleep(BAN_SLEEP_DELAY)
		else:
			break

	try:
		volume = int(data['volume'].replace(',',''))
	except:
		return False

	if volume < MIN_VOLUME:
		return False

	return volume
'''
def get_valid_items_by_profit_filter(session):
	for item in valid_items:
		app_id = item['asset_description']['appid']
		hash_name = item['hash_name']
		name = item['name']
		histogram = None
		histogram_flag = False


		volume = get_valid_items_by_volume_filter(session=session, app_id=app_id, item_name=hash_name)
		time.sleep(SLEEP_DELAY)
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
				time.sleep(BAN_SLEEP_DELAY)
			else:
				break

		start_time = time.time()
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

			price_selection_success = False

			while True: # цикл подбора оптимальных цен
				biggest_counter = 0
				sum_buy_count = 0
				for counter, i in enumerate(histogram['buy_order_graph']):
					sum_buy_count += int(i[1])#
					if int(i[1]) > biggest_counter: 
						biggest_counter = int(i[1])
						if counter != 0:
							buy_price = float(histogram['buy_order_graph'][counter - 1][0])
					if counter + 1 >= depth:
						break

				biggest_counter = 0
				sum_sell_count = 0
				for counter, i in enumerate(histogram['sell_order_graph']):
					sum_sell_count += int(i[1])#
					if int(i[1]) > biggest_counter: 
						biggest_counter = int(i[1])
						if counter < len(histogram['sell_order_graph']) - 1:
							if int(histogram['sell_order_graph'][counter + 1][1]) > int(histogram['sell_order_graph'][counter][1]):
								sell_price = float(histogram['sell_order_graph'][counter][0])
							else:
								sell_price = float(histogram['sell_order_graph'][counter + 1][0])
					if counter + 1 >= depth:
						break

				if sum_sell_count + sum_buy_count < volume * PARAM:
					price_selection_success = True
					break
				else: 
					depth -= 2

				if depth < 1:
					break

		if not price_selection_success:
			continue

		percent = ((sell_price - sell_price * 0.13 - buy_price)/sell_price) * 100
		print(hash_name, buy_price, sell_price, percent, time.time() - start_time)
		if percent >= MIN_PROFIT:
			#valid_items.remove(item)
			time.sleep(SLEEP_DELAY)
			valid_data.append([name, sell_price, buy_price, percent])
			#print(hash_name, buy_price, sell_price, time.time() - start_time)
			continue
		time.sleep(SLEEP_DELAY)
'''
def get_valid_items_by_profit_filter(session):
	for item in valid_items:
		app_id = item['asset_description']['appid']
		hash_name = item['hash_name']
		name = item['name']
		histogram = None
		histogram_flag = False


		volume = get_valid_items_by_volume_filter(session=session, app_id=app_id, item_name=hash_name)
		time.sleep(SLEEP_DELAY)
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
										if sum_sell_count + sum_buy_count < volume * PARAM:
											percent = ((sell_price - sell_price * 0.13 - buy_price)/sell_price) * 100
											stored_prices[percent] = {'buy_price':buy_price, 'sell_price':sell_price}

									else:
										sell_price = float(histogram['sell_order_graph'][counter + 1][0])
										if sum_sell_count + sum_buy_count < volume * PARAM:
											percent = ((sell_price - sell_price * 0.13 - buy_price)/sell_price) * 100
											stored_prices[percent] = {'buy_price':buy_price, 'sell_price':sell_price}
			max_precent = 0
			try:
				max_precent = max(stored_prices)
			except:
				continue
				
			print(hash_name, stored_prices[max_precent]['buy_price'], stored_prices[max_precent]['sell_price'], max_precent)
			if max_precent >= MIN_PROFIT:
				#valid_items.remove(item)
				time.sleep(SLEEP_DELAY)
				valid_data.append([name, stored_prices[max_precent]['sell_price'], stored_prices[max_precent]['buy_price'], max_precent])
				#print(hash_name, buy_price, sell_price, time.time() - start_time)
				continue
			time.sleep(SLEEP_DELAY)

def get_minimal_item_data(session):
	for item in valid_items:
		app_id = item['asset_description']['appid']
		hash_name = item['hash_name']
		name = item['name']

		data = get_item_data(session=session, app_id=app_id, item_name=hash_name)
		time.sleep(SLEEP_DELAY)
		if not data:
			valid_items.remove(item)
			continue
		elif not data['success']:
			valid_items.remove(item)
			continue

		volume = int(data['volume'].replace(',',''))
		min_price = data['lowest_price']
		median_price = data['median_price']
		if volume < MIN_VOLUME:
			valid_items.remove(item)
			continue
			
		print(hash_name, volume, min_price, median_price)
		time.sleep(SLEEP_DELAY)
		valid_data.append([name, volume, min_price, median_price])

def get_settings():
	with open('config.json', 'r') as f:
		data = json.load(f)
		global MAX_PRICE
		MAX_PRICE = data['max_price']
		global MIN_VOLUME
		MIN_VOLUME = data['min_volume']
		global MIN_PROFIT
		MIN_PROFIT = data['min_profit']

def remove_dublicates_in_valid_data():
	global valid_data
	lst = [i[0] for i in valid_data]
	for i in valid_data:
		if lst.count(i[0]) > 1:
			valid_data.remove(i)


def main():
	session = requests.Session()
	session.get('https://steamcommunity.com/market/')
	session.headers.update(headers)
	session.cookies.update(cookies)

	#get_settings()

	print('Started')
	get_valid_items_by_price_filter(session=session)
	print('getting volume', str(len(valid_items)))
	'''
	get_valid_items_by_volume_filter(session=session)
	print('gettint profit', str(len(valid_items)))
	'''
	#get_valid_items_by_profit_filter(session=session)
	get_minimal_item_data(session=session)
	print(f'stored items count {len(valid_data)}')

	wb = openpyxl.Workbook()
	sheet = wb['Sheet']

	#head = ['Название','Цена продажи','Цена покупки','Профит(%)']
	head = ['Name', 'Volume', 'Lowest price', 'Median price']
	sheet.append(head)

	remove_dublicates_in_valid_data()

	for counter, item in enumerate(valid_data):
		sheet.append(item)

	wb.save('data.xlsx')


if __name__ == "__main__":
	main()