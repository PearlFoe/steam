from config import *

from bs4 import BeautifulSoup as bs
import requests
import time

def get_full_page_data(session, page_number, app_id):
	if page_number != 0:
		page = str(page_number * 10)
	else:
		page = '00'

	url = f'https://steamcommunity.com/market/search/render/?query=&start={page}&count=10&search_descriptions=0&sort_column=price&sort_dir=asc&appid={app_id}&norender=1'
	#url = f'https://steamcommunity.com/market/search/render/?query=&start={page}&count=10&search_descriptions=0&sort_column=price&sort_dir=asc&norender=1'
	data = session.get(url).json()

	return data

def get_item_list(session, page_number, app_id):
	if page_number != 0:
		page = str(page_number * 10)
	else:
		page = '00'

	url = f'https://steamcommunity.com/market/search/render/?query=&start={page}&count=10&search_descriptions=0&sort_column=price&sort_dir=asc&appid={app_id}&norender=1'
	#url = f'https://steamcommunity.com/market/search/render/?query=&key={api_key}&start={page}&count=10&search_descriptions=0&sort_column=price&sort_dir=asc&norender=1'
	data = session.get(url).json()
	
	return data['results']

def get_item_data(session, app_id, item_name):
	url = f'https://steamcommunity.com/market/priceoverview/?appid={app_id}&market_hash_name={item_name}&currency=5'
	#при обычном запросе без cookies цены тоже возращаются в рублях
	#data = session.get(url).json()
	data = requests.get(url).json()


	return data

def get_item_price_histogram(session, app_id, item_name):
	url = f'https://steamcommunity.com/market/listings/{app_id}/{item_name}'
	response = requests.get(url)
	data = bs(response.text, 'lxml').find_all('script')
	item_nameid = 0
	for i in data:
		if 'Market_LoadOrderSpread' in str(i):
			item_nameid = str(i).split('Market_LoadOrderSpread')[-1].split('( ')[-1].split(' )')[0]
			break

	time.sleep(SLEEP_DELAY)
	url = f'https://steamcommunity.com/market/itemordershistogram?country=RU&language=russian&currency=5&item_nameid={item_nameid}&two_factor=0&norender=1'
	data = session.get(url).json()

	return data



