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


def closest_banks(user_location):
	banks = []
	user_location = user_location.split(", ")
	for address, location in bank_locations.items():
		if within_km(user_location, location):
			banks.append(address)
	return banks


def within_km(user_location, bank_location):
	bank_location = [float(i) for i in bank_location]
	user_location = [float(i) for i in user_location]
	lon1, lat1, lon2, lat2 = map(radians, [bank_location[1], bank_location[0], user_location[1], user_location[0]])
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
	course = bank.select("td > span.first_curr")[c_index].getText()
	return "\n".join([title, phone, address, course])


def currency_response(user_location, operation, curr):
	closest_b = closest_banks(user_location)
	banks = soup_page.select("tr.currency_row_1")
	response = [course_info(b, operation, curr) for b in banks if b.select("div.address")[0].getText() in closest_b]
	return response
	


user_location = input("Координаты юзера: ")
curr = input("Валюта: ")
operation = input("Тип операции: ")

print(("\n"+(("*")*26)+"\n").join(currency_response(user_location, operation, curr)))