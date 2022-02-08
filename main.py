from urllib.parse import urlparse, urlsplit, unquote
import requests
import os
import datetime
from dotenv import load_dotenv

from telegram.ext import Updater, ExtBot


def add_0(item: str):
    return item if len(item) == 2 else f'0{item}'


def get_response(url, options=None):
    headers = {
        'User-Agent': 'my-first-bot / 1.0'
    }
    response = requests.get(url, headers=headers, params=options)
    response.raise_for_status()
    return response


def get_file_extension(file_link):
    parsed_link = urlsplit(file_link)
    path = parsed_link.path
    path = unquote(path)
    filename = os.path.split(path)[1]
    return os.path.splitext(filename)[1]


def download_image(path, url, options=None):
    response = get_response(url, options)
    with open(path, mode='wb') as file:
        file.write(response.content)


def fetch_spacex_last_launch(directory, url):
    response = get_response(url)
    images_links = []
    data = response.json()
    flag = False
    for launch in data:
        for key, value in launch['links']['flickr'].items():
            if key == 'original':
                flag = len(value) > 0
            if flag:
                images_links.extend(value)
                break

    for i_link in images_links:
        parsed_link = urlparse(i_link)
        start = parsed_link.path.rfind('/') + 1
        filename = parsed_link.path[start:]
        path = os.path.abspath(os.path.join(directory, filename))
        download_image(path, i_link)


def fetch_nasa_images(directory, url):
    query_params = {
        'api_key': os.getenv('NASA_KEY'),
        'count': '40'
    }
    response = get_response(url, query_params)
    data = response.json()
    images_links = [data_unit[key] for data_unit in data for key in data_unit if key == 'hdurl']
    for i, i_link in enumerate(images_links):
        filename = f'nasa_{i + 1}{get_file_extension(i_link)}'
        path = os.path.abspath(os.path.join(directory, filename))
        download_image(path, i_link, query_params)


def fetch_nasa_epic_images(directory, url):
    image_date, image_name, image_url = '', '', ''
    query_params = {
        'api_key': os.getenv('NASA_KEY')
    }
    response = get_response(url, query_params)
    limit_response = response.json()[:10]

    for i, response_unit in enumerate(limit_response):
        for k, v in response_unit.items():
            if k == 'date':
                image_date = datetime.datetime.fromisoformat(v)
            if k == 'image':
                image_name = v
        image_url = f'https://api.nasa.gov/EPIC/archive/natural/{image_date.year}/{add_0(str(image_date.month))}' \
                    f'/{add_0(str(image_date.day))}/png/{image_name}.png'

        filename = f'nasa_epic_{i + 1}.png'
        path = os.path.abspath(os.path.join(directory, filename))
        download_image(path, image_url, query_params)


def main():
    url_spacex = 'https://api.spacexdata.com/v4/launches/'
    directory = 'images'
    # nasa_directory = 'nasa_directory'
    # nasa_epic_directory = 'nasa_epic_directory'
    nasa_url = 'https://api.nasa.gov/planetary/apod'
    nasa_epic_url = 'https://api.nasa.gov/EPIC/api/natural'

    try:
        load_dotenv()
        if not os.path.exists(directory):
            os.makedirs(directory)

        # fetch_spacex_last_launch(directory, url_spacex)
        # fetch_nasa_images(directory, nasa_url)
        # fetch_nasa_epic_images(directory, nasa_epic_url)
        telegram_token = os.getenv('TELEGRAM_KEY')
        chat_id = os.getenv('CHAT_ID')
        bot = ExtBot(token=telegram_token)
        bot.send_message(chat_id, 'Hi!')
        with open('/home/serge/PycharmProjects/training/devman/dvnm-api-4/images/nasa_epic_9.png', mode='rb') as photo:
            bot.send_photo(chat_id, photo)
        # updater = Updater(telegram_token, use_context=True)
        # dispatcher = updater.dispatcher
        # updater.start_polling()
        # updater.idle()


    except (requests.exceptions.HTTPError,
            requests.exceptions.InvalidSchema,
            requests.exceptions.ConnectionError) as e:
        error_data = e.response
        error_code = error_data.status_code
        if error_code == 400:
            print('Вы ошиблись при вводе сайта')
        elif error_code == 403:
            print('Доступ запрещён. Проверьте токен')
        else:
            print('Ошибка доступа: ', error_code)
    except FileNotFoundError as e:
        print(e)


if __name__ == '__main__':
    main()
