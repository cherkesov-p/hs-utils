#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Any

import os
import csv
import sys
import getpass
import logging
import requests
from lxml import html
from datetime import datetime, timedelta

logging.basicConfig(format='[%(asctime)s] [%(levelname).1s] %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO,
                    stream=sys.stdout)


class Swrve_connect:
    session: requests.Session
    platforms: dict[str, str] = {
        'iOS': '4698',
        'Android': '4699',
        'Facebook': '30745',
    }
    platforms_token: dict[str, str] = {}

    def __init__(self):
        # Запрашиваем у пользователя логин и пароль
        self.session = requests.Session()
        logging.info('[SWRVE] authenticate with username and password')
        login: str = input('Login (e-mail): ')
        password: str = getpass.getpass('Password: ')
        self._auth(login, password)

    def _auth(self, login: str, password: str):
        # Запрашиваем страницу авторизации и получаем скрытое поле c токеном
        r = self.session.get('https://dashboard.swrve.com/login', cookies=self.session.cookies)
        text = html.fromstring(r.text)

        # Авторизуемся на портале
        data = {
            'developer_session[email]': login,
            'developer_session[password]': password,
            'authenticity_token': text.xpath('.//input[@name="authenticity_token"]/@value')[0],
        }
        self.session.post('https://dashboard.swrve.com/login', data=data, cookies=self.session.cookies)
        logging.info('Auth from SWRVE')

    def _csrf(self, url: str, name: str = 'csrf-token') -> str:
        # Запрашиваем страницу и извлекаем csrf-токен из мета
        r = self.session.get(url, cookies=self.session.cookies)
        text = html.fromstring(r.text)

        return str(text.xpath('.//meta[@name="' + name + '"]/@content')[0])

    def set_annotation(self, date: Any, title: str, platform: str):
        data = {
            'utf8': '✓',
            'annotation[date]': "{:%m-%d-%Y}".format(date),
            'annotation[name]': title,
            'commit': 'Add Annotation',
        }

        # Проверяем наличие токена для платформы, чтобы не перезапрашивать
        if platform not in self.platforms_token:
            self.platforms_token[platform] = self._csrf('https://dashboard.swrve.com/apps/' + self.platforms[platform] + '/settings/report')

        csrf = self.platforms_token[platform]
        # Отправляем аннотацию на сайт
        requests.post(
            'https://dashboard.swrve.com/apps/' + self.platforms[platform] + '/annotations',
            data=data,
            cookies=self.session.cookies,
            headers={'x-csrf-token': csrf}
        )
        logging.info('"' + data['annotation[name]'] + '" от ' + "{:%d-%m-%Y}".format(date) + ' для ' + platform)


def read_events(filename: str, swrve: Swrve_connect, platform: str):
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            # Пропускаем заголовок таблицы
            if reader.line_num == 1:
                continue

            start = datetime.date(datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%S"))
            end = datetime.date(datetime.strptime(row[1], "%Y-%m-%dT%H:%M:%S"))
            # Выбираем события попапшие в наш диапазон
            if start >= start_date and start <= end_date:
                # Исключем отдельные события
                title = row[2]
                if title == 'Копилка' or title == 'Турнир Чемпионов':
                    continue
                # Считаем продолжительность
                title = title + ' (' + str((end - start).days) + 'д)'

                swrve.set_annotation(start, title, platform)


swrve = Swrve_connect()

# Выборка от текущей даты и на неделю вперёд
start_date = datetime.date(datetime.now())
end_date = datetime.date(datetime.now() + timedelta(days=6))

data_path = os.path.join(os.getcwd(), 'data')

read_events(os.path.join(data_path, 'events_ios.csv'), swrve, 'iOS')
read_events(os.path.join(data_path, 'events_android.csv'), swrve, 'Android')
read_events(os.path.join(data_path, 'events_facebook.csv'), swrve, 'Facebook')


logging.info('Done')
