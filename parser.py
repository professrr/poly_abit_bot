import grequests
import time
import json
from sys import getsizeof
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb://mongodb11:27017/')

exceptions = []

# IMPORTANT! Use global var exceptions = []

def parseWithExc(urls, batch_size=2, delay=0):
    # exceptions = []
    global exceptions
    data = []
    i = 0 
    while len(urls) > 0:
        print("Trying parse with attempt №", i, "; URLs count =", len(urls))
        data.append(parse(urls, batch_size, delay))
        print("Parsed with attempt №", i, "; Exceptions count=", len(exceptions))
        urls = exceptions
        exceptions = []
        i += 1
    return data

def parse(urlss, batch_size, delay):
    batched_urls = chunks(urlss, batch_size)
    result = []
    i=0
    for urls in batched_urls:
        rs = (grequests.get(u['url']) for u in urls)
        for r in grequests.map(rs, exception_handler=exception_handlerr):
            i+=1
            # print(dir(r))
            # print("Status =",r.status_code, "; Server date =" ,r.headers['Date'])
            if r is not None:
                print("Request №", i, "Status =", r.status_code)
                result.append(r)
            else:
                print("Request №", i, "Status trouble")
        time.sleep(delay)
    return result

# IMPORTANT! Use global var exceptions = []
def exception_handlerr(request, exception):
    global exceptions
    print('-------------------------------------------')
    print("Request failed", request.url)
    # exception contains what's fucked up
    # to see props of exception use print(dir())
    print(exception.request.url)
    parsed_url = urlparse(exception.request.url)
    exceptions.append({
        "url": request.url,
    })
    print('-------------------------------------------')

def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))

urls = [{
    "url": 'https://www.spbstu.ru/abit/admission-campaign/ajax.php?ab_email=Y&ab_action=getHtmlRangedItems&groupId=230&concursForm=1%2C2&confirm=all',
},{
    "url": 'https://www.spbstu.ru/abit/admission-campaign/ajax.php?ab_email=Y&ab_action=getHtmlRangedItems&groupId=229&concursForm=1%2C2&confirm=all',
}]

while(True):
    start = time.time()
    data_to_insert = []
    data = parseWithExc(urls)
    for dd in data:
        for d in dd:
            soup = BeautifulSoup(d.text, 'html.parser')
            table = soup.find("tbody").find_all("tr")
            parsed_url = urlparse(d.url)
            users = []
            for row in table:
                cells = row.find_all("td")
                users.append({
                    "place": cells[0].text,
                    "name": cells[1].text,
                    "sum": cells[2].text,
                    "math": cells[3].text,
                    "it": cells[4].text,
                    "rus": cells[5].text,
                    "extra": cells[6].text,
                    "approve": cells[7].text.strip().lower(),
                    "hit": cells[8].text if cells[8].text != "" else "нет"
                })
            data_to_insert.append({
                "params": parse_qs(parsed_url.query),
                "poly_date": soup.find("h3").text,
                "server_date": (datetime.now() + timedelta(hours=3)).strftime("%H:%M:%S"),
                "data": users
            })
    with client:
        db = client.monitor_poly
        res = db.poly_data.insert_many(data_to_insert)
        print(res)
    # with open('data.json', 'w', encoding='utf-8') as f:
    #     json.dump(data_to_insert, f, ensure_ascii=False, indent=4)
    end = time.time()
    time.sleep(10)
    print("Fineshed parsing! Time =", end - start)
