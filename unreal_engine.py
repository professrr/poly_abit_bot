from pymongo import MongoClient
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process
import json

client = MongoClient('mongodb://localhost:27017/')

def showRelatedNames(name, client):
    with client:
        db = client.monitor_poly
        res = db.poly_data.find().limit(2).sort('_id',-1)
        max = {
            "230":{"value": -1},
            "229":{"value": -1}
        }
        for users in res:
            print('-------------------------------------')
            for user in users["data"]:
                tmp = fuzz.token_sort_ratio(user["name"], name)
                groupId = users["params"]["groupId"][0]
                if tmp > max[groupId]["value"]:
                    max[groupId]["value"] = tmp
                    max[groupId]["name"] = user["name"]
                    max[groupId]["fake"] = name
        return max

# def initialInsertUser(telegram_info, max, client):
    # with client:
    #     db = client.monitor_poly
    #     try{
    #         db.users.insertOne({
    #             "watcher_id": telegram_info["id"],
    #             "watcher_username": telegram_info["username"],
    #             "watch_info": max
    #        })
    #        return "Наблюдение сохранено!"
    #     }
    #     catch(e) {
    #         return "Ошибка соххранения наблюдения"
    #     }

        
with client:
    db = client.monitor_poly
    res = db.users.find()
    arr = []
    for item in res:
        arr.append(item)
    with open('res.json', 'w', encoding='utf-8') as f:
        json.dump(arr, f, ensure_ascii=False, indent=4)
# showRelatedNames("Антон семенов", client)
