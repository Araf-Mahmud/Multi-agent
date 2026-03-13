import json
import requests

response = requests.get(url="https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql")

if response.status_code == 200:
    # print(response.json())
    print(response.headers.get('Content-Type',""))
    data = response.text
    
    with open('sql-data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)