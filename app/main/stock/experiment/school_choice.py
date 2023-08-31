import requests
import time

from app.main.db.mongo import db
if __name__ == "__main__":
    r = requests.get("https://static-data.gaokao.cn/www/2.0/school/name.json")
    data = r.json()['data']

    schools = [{"school_id":d['school_id'],"name":d['name']} for d in data if d['type'] == '6001']

    print(len(schools))

    url = "https://static-data.gaokao.cn/www/2.0/schoolspecialindex/2021/{}/33/3/17/1.json"

    for school in schools:
        school_id = school['school_id']
        name = school['name']
        target_url = url.format(school_id)
        r = requests.get(target_url)
        if r.text == '""':
            continue
        time.sleep(0.2)
        datas = r.json()['data']['item']
        for data in datas:
            score_min = int(data['min'])
            rank_min = int(data['min_section'])
            spname = data['spname']

            print(name,spname,rank_min,score_min)
            db.school.insert(dict(
                name=name,
                spname=spname,
                rank_min=rank_min,
                score_min=score_min
            ))

