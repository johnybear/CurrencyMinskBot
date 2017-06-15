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

def within_km(user_lockation, bank_location):
	pass

def currency_response(operation, curr):
	banks = soup_page.select("tr.currency_row_1")
	for b in banks:
		print(course_info(b, operation, curr)+"\n")

def course_info(bank, operation, curr):
	c_index = CURRENCY_INDEX[(operation, curr)]
	title = bank.select("div.ttl > a")[0].getText()
	phone = bank.select("div.tel")[0].getText()
	address = bank.select("div.address")[0].getText() or "No phone"
	course = bank.select("td > span.first_curr")[c_index].getText()
	return "\n".join([title, phone, address, course])

