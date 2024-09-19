import requests
from bs4 import BeautifulSoup
import json
from time import sleep
from random import randrange


def is_blocked(response):
    # Проверка кода состояния
    if response.status_code == 403:
        print("Доступ запрещен (403).")
        return True
    if response.status_code == 429:
        print("Превышен лимит запросов (429).")
        return True
    if "captcha" in response.text.lower():
        print("Капча обнаружена, вероятно, блокировка.")
        return True
    return False


persons_url_list = []
for i in range(0, 760, 12):
    url = f"https://www.bundestag.de/ajax/filterlist/en/members/863330-863330?limit=12&noFilterSet=true&offset={i}"

    q = requests.get(url)

    if is_blocked(q):
        print("Вы заблокированы!")
        break

    result = q.content

    soup = BeautifulSoup(result, "lxml")
    persons = soup.find_all("a")
    for person in persons:
        person_page_url = person.get("href")
        persons_url_list.append(person_page_url)

with open("persons_url_list.txt", "a", encoding="utf-8") as file:
    for line in persons_url_list:
        file.write(line + "\n")


data_dict = []
count = 0

with open("persons_url_list.txt", encoding="utf-8") as file:

    lines = [line.strip() for line in file.readlines()]

    for line in lines:
        q = requests.get(line)
        result = q.content

        soup = BeautifulSoup(result, "lxml")

        # Поиск имени
        person_tag = soup.find(class_="bt-biografie-name")
        if person_tag:
            person = person_tag.find("h3").text
            if person:
                person_name_company = person.strip().split(",")
                person_name = person_name_company[0]
                person_company = person_name_company[1].strip()
            else:
                print("Сотрудник не найден")
        else:
            print("Биографическая информация не найдена")

        social_networks = soup.find_all(class_="bt-link-extern")

        social_networks_urls = []

        for item in social_networks:
            social_networks_urls.append(item.get("href"))

        data = {
            "person_name": person_name,
            "person_company": person_company,
            "social_networks": social_networks_urls,
        }

        count += 1
        if not is_blocked(q):
            print(f"#{count}: {line}. Запись выполнена")

        data_dict.append(data)

        with open("data.json", "w", encoding="utf-8-sig") as json_file:
            json.dump(data_dict, json_file, indent=4, ensure_ascii=False)

        sleep(randrange(1, 3))
