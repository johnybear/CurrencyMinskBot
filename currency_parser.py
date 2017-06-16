import json
from math import radians, cos, sin, asin, sqrt
from bs4 import BeautifulSoup
import requests

CURRENCY_INDEX = {
	("buy", "usd"):0,
	("sell", "usd"):1,
	("buy", "eur"):2,
	("sell", "eur"):3,
	("buy", "rub"):4,
	("sell", "rub"):5
}

page_html = requests.get("https://myfin.by/currency/minsk").text
soup_page = BeautifulSoup(page_html, 'html.parser')
with open("bank_locations.json", "r") as b:
	bank_locations= json.load(b)


def within_km(user_location, bank_location):
	b_lat, b_long = tuple(map(float, bank_location))
	u_lat, u_long = user_location.latitude, user_location.longitude
	lon1, lat1, lon2, lat2 = map(radians, [b_long, b_lat, u_long, u_lat])
	# haversine formula 
	dlon = lon2 - lon1 
	dlat = lat2 - lat1 
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a)) 
	km = 6367 * c
	return km <= 1

def course_info(bank, operation, curr):
	c_index = CURRENCY_INDEX[(operation, curr)]
	title = bank.select("div.ttl > a")[0].getText()
	phone = bank.select("div.tel")[0].getText()
	address = bank.select("div.address")[0].getText()
	course = "курс обмена: " + bank.select("td > span.first_curr")[c_index].getText()
	return [title, phone, address, course]


def stringify_response(curr_list):
	response = sorted(curr_list, key=lambda x: x[3])
	if operation == "buy":
		response.reverse()
	response = map("\n".join, response)
	response = map(lambda x: x.strip(), response)#remove empty values from each elem
	response = ("\n"+(("*")*26)+"\n").join(response)
	return response


def currency_response(user_location, operation, curr):
	closest_banks = [ad for ad, loc in bank_locations.items() if within_km(user_location, location)]
	banks = soup_page.select("tr.currency_row_1")
	unsorted_curr_list = [course_info(b, operation, curr) for b in banks if b.select("div.address")[0].getText() in closest_banks]
	response = stringify_response(unsorted_curr_list)
	return response
	
