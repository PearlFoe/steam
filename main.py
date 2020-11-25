from steam import *

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

def get_valid_items_by_price_filter():
	page = 0
	while True:
		flag = False
		items = None

		while True:
			try:
				items = item_list(page)
				break
			except Exception:
				print('got ban, waiting 3 min')
				time.sleep(180)

		for item in items:
			if item["sell_price"] <= MAX_PRICE and item["sell_price"] != 0:
				print(item['name'] ,item["sell_price"])
				#print(item['name'])
				flag = True
				valid_items.append(item)
			elif item["sell_price"] == 0:
				flag = True

		#print(items[0]['name'])
		if not flag:
			time.sleep(10)
			break

		page += 1
		print(f'page {page}\n')
		time.sleep(10)
		
def get_valid_items_by_volume_filter():
	for item in valid_items:
		app_id = item['asset_description']['appid']
		name = item['name']
		data = get_item_data(app_id, name)
		volume = 0
		try:
			volume = int(ata['volume'].replace(',',''))
		except:
			valid_items.remove(item)
			time.sleep(3)
			continue

		if volume < MIN_VOLUME:
			valid_items.remove(item)
		time.sleep(3)

def get_valid_items_by_profit_filter():
	for item in valid_items:
		app_id = item['asset_description']['appid']
		name = item['name']

		histogram = get_item_price_histogram(app_id, name)
		sell_info = None
		buy_info = None
		try:
			buy_info = int(histogram['highest_buy_order'])
			sell_info = int(histogram['lowest_sell_order'])
		except Exception:
			continue
		

		percent = ((sell_info - sell_info * 0.13 - buy_info)/sell_info) * 100

		if percent >= MIN_PROFIT:
			#valid_items.remove(item)
			time.sleep(3)
			valid_data.append([name, sell_info, buy_info, percent])
			continue
		time.sleep(3)


		'''
		try:
			buy_info = histogram['buy_order_graph'][:15]
			sell_info = histogram['sell_order_graph'][:15]
		except:
			continue
		
		buy_summ = 0
		sell_sum = 0
		if len(sell_info) == 0 or len(buy_info) == 0:
			continue

		if len(sell_info) <= len(buy_info):
			for i in range(len(sell_info)):
				buy_summ += buy_info[i][0]
				sell_sum += sell_info[i][0]
		else:
			for i in range(len(buy_info)):
				buy_summ += buy_info[i][0]
				sell_sum += sell_info[i][0]


		midle_buy_price = buy_summ/len(buy_info)
		midle_sell_price = sell_sum/len(sell_info)

		percent = ((midle_sell_price - midle_sell_price * 0.13 - midle_buy_price)/midle_sell_price) * 100
		

		if percent >= MIN_PROFIT:
			valid_items.remove(item)
			time.sleep(3)
			valid_data.append([name, midle_sell_price, midle_buy_price, percent])
			continue
		time.sleep(3)
		'''
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

	get_settings()

	print('Started')
	get_valid_items_by_price_filter()
	print('getting volume', str(len(valid_items)))
	get_valid_items_by_volume_filter()
	print('gettint profit', str(len(valid_items)))
	get_valid_items_by_profit_filter()

	wb = openpyxl.Workbook()
	sheet = wb['Sheet']

	head = ['Название','Цена продажи','Цена покупки','Профит(%)']
	sheet.append(head)
	
	for counter, item in enumerate(valid_data):
		sheet.append(item)

	wb.save('data.xlsx')


if __name__ == "__main__":
	main()



