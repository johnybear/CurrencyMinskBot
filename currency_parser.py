import json
from math import radians, cos, sin, asin, sqrt
from bs4 import BeautifulSoup
import requests

CURRENCY_INDEX = {
    ("buy", "USD"):0,
    ("sell", "USD"):1,
    ("buy", "EUR"):2,
    ("sell", "EUR"):3,
    ("buy", "RUB"):4,
    ("sell", "RUB"):5
}

user_requests = {}

page_html = requests.get("https://myfin.by/currency/minsk").text 
SOUP_PAGE = BeautifulSoup(page_html, 'html.parser')
with open("bank_locations.json", "r") as b:
    BANK_LOCATIONS= json.load(b)

def distance(user_location, bank_location):
    b_lat, b_long = bank_location["latitude"], bank_location["longitude"]
    u_lat, u_long = user_location.latitude, user_location.longitude
    lon1, lat1, lon2, lat2 = map(radians, [b_long, b_lat, u_long, u_lat])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km


def within_km(user_location, bank_location):
    km = distance(user_location, bank_location)
    return km <= 1

def course_info(bank, operation, curr):
    c_index = CURRENCY_INDEX[(operation, curr)]
    if curr=="RUB":
        curr="100 RUB"
    else:
        curr="1 "+curr
    title = bank.select("div.ttl > a")[0].getText()
    phone = bank.select("div.tel")[0].getText()
    address = bank.select("div.address")[0].getText()
    course = "%s за %s BYN" % (curr,
                           bank.select("td > span.first_curr")[c_index].getText())
    return [title, phone, address, course]


def stringify_response(curr_list, operation):
    response = sorted(curr_list, key=lambda x: x[3])
    if operation == "buy":
        response.reverse()
    response = map("\n".join, response)
    response = map(lambda x: x.strip(), response)#remove empty values from each elem
    response = ("\n"+(("*")*26)+"\n").join(response)
    operation = "БАНКИ ПРОДАЮТ\n\n" if operation=='sell' else "БАНКИ ПОКУПАЮТ\n\n"
    response = operation+response
    return response


def currency_response(user_location, operation, currency):
    closest_banks = [ad for ad, loc in BANK_LOCATIONS.items() if within_km(user_location, loc)]
    if not closest_banks:
        distances = ((ad, distance(user_location, loc)) for ad, loc in BANK_LOCATIONS.items())
        distances = sorted(distances, key=lambda x: x[1])[0:3]
        closest_banks = [ad[0] for ad in distances]
    banks = SOUP_PAGE.select("tr.currency_row_1")
    unsorted_curr_list = [course_info(b, operation, currency) for b in banks if b.select("div.address")[0].getText() in closest_banks]
    response = stringify_response(unsorted_curr_list, operation)
    return response