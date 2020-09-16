from fuzzywuzzy import fuzz 
from fuzzywuzzy import process
import json

# client = MongoClient('mongodb://localhost:27017/')

#returning an arr of users
def countSubs(id_user, client):
    user = getNamesByUser(id_user, client)
    print(user["watch_info"]["230"]["name"])
    with client:
        db = client.monitor_poly
        res = db.users_new.find({"watch_info.230.name": user["watch_info"]["230"]["name"]}).sort('_id',-1)
        return res
        



def getNamesByUser(id_user, client):
    with client:
        db = client.monitor_poly
        res = db.users_new.find({"watcher_id": id_user}).limit(1).sort('_id',-1)
        a = {}
        for r in res:
            a = r
        return a


#id = 0 if group = 230
#id = 1 if group = 229
def calculate(id, name, id_user, client):
    user = getNamesByUser(id_user, client)
    with client:
        # print(user)
        db = client.monitor_poly
        res = db.poly_data.find().limit(2).sort('_id',-1)
        i = 0
        counter_yes = 0 #есть согласие
        counter_maybe = 0 #если нет согласия
        counter_maybe_maybe = 0 #если согл. по другому направ, он может изменить
        if id == 229:
            while (res[0]["data"][i]["name"] != user["watch_info"]["229"]["name"]):
                # "да"
                # "нет"
                # "согласие по др. напр."
                # "зачислена на др. напр."
                # "зачислен на др. напр."
                if res[0]["data"][i]["hit"] == "да":
                    counter_yes += 1
                if res[0]["data"][i]["hit"] == "нет" or res[0]["data"][i]["hit"] == "да":
                    counter_maybe += 1
                if res[0]["data"][i]["hit"] == "согласие по др. напр." or res[0]["data"][i]["hit"] == "нет" or res[0]["data"][i]["hit"] == "да":
                    counter_maybe_maybe += 1
                i += 1
            return {
                "place": res[0]["data"][i]["place"],
                "name": res[0]["data"][i]["name"],
                "sum": res[0]["data"][i]["sum"],
                "math": res[0]["data"][i]["math"],
                "it": res[0]["data"][i]["it"],
                "rus": res[0]["data"][i]["rus"],
                "extra": res[0]["data"][i]["extra"],
                "approve": res[0]["data"][i]["approve"],
                "hit": res[0]["data"][i]["hit"],
                "counter_yes": counter_yes,
                "counter_maybe": counter_maybe,
                "counter_maybe_maybe": counter_maybe_maybe,
                "poly_date": res[0]["poly_date"],
                "server_date": res[0]["server_date"],
                "group_name": name
            }
        elif id == 230:
            # print(res[1]["data"][0]["name"])
            while (res[1]["data"][i]["name"] != user["watch_info"]["230"]["name"]):
                # "да"
                # "нет"
                # "согласие по др. напр."
                # "зачислена на др. напр."
                # "зачислен на др. напр."
                if res[1]["data"][i]["hit"] == "да":
                    counter_yes += 1
                if res[1]["data"][i]["hit"] == "нет" or res[1]["data"][i]["hit"] == "да":
                    counter_maybe += 1
                if res[1]["data"][i]["hit"] == "согласие по др. напр." or res[1]["data"][i]["hit"] == "нет" or res[1]["data"][i]["hit"] == "да":
                    counter_maybe_maybe += 1
                i += 1
            return {
                "place": res[1]["data"][i]["place"],
                "name": res[1]["data"][i]["name"],
                "sum": res[1]["data"][i]["sum"],
                "math": res[1]["data"][i]["math"],
                "it": res[1]["data"][i]["it"],
                "rus": res[1]["data"][i]["rus"],
                "extra": res[1]["data"][i]["extra"],
                "approve": res[1]["data"][i]["approve"],
                "hit": res[1]["data"][i]["hit"],
                "counter_yes": counter_yes+1,
                "counter_maybe": counter_maybe+1,
                "counter_maybe_maybe": counter_maybe_maybe+1,
                "poly_date": res[1]["poly_date"],
                "server_date": res[1]["server_date"],
                "group_name": name
            }

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

def initialInsertUser(telegram_info, max, client):
    with client:
        db = client.monitor_poly
        res = db.users_new.insert_one({
            "watcher_id": telegram_info["id"],
            # "watcher_url": telegram_info["url"],
            "watcher_first_name": telegram_info["first_name"],
            "watcher_last_name": telegram_info["last_name"],
            "watcher_username": telegram_info["username"],
            "watch_info": max["max"]
        })
        if res:
            return "Наблюдение сохранено!\nЛови доступ к меню\n👉🏼 /menu"
        else:
            return "Ошибка сохранения наблюдения"

# with open('countSubs.json', 'w', encoding='utf-8') as f:
#         json.dump(getNamesByUser(78795079, client), f, ensure_ascii=False, indent=4)
