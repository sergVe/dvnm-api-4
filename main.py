import time
from urllib.parse import urlparse, urlsplit, unquote
import requests
import os
import datetime
from dotenv import load_dotenv
from telegram import error
from telegram.ext import ExtBot


def get_file_extension(file_link):
    parsed_link = urlsplit(file_link)
    path = parsed_link.path
    path = unquote(path)
    return os.path.splitext(path)[1]


def download_image(path, url, options=None):
    headers = {
        'User-Agent': 'my-first-bot / 1.0'
    }
    response = requests.get(url, headers=headers, params=options)
    response.raise_for_status()

    with open(path, mode='wb') as file:
        file.write(response.content)


def fetch_spacex_last_launch(directory):
    url = 'https://api.spacexdata.com/v4/launches/'
    headers = {
        'User-Agent': 'my-first-bot / 1.0'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    images_links = []
    launches = response.json()

    for launch in launches:
        desired_images = launch['links']['flickr']
        images_addresses = desired_images.get('original')
        if images_addresses:
            images_links.extend(images_addresses)
            break

    for link in images_links:
        parsed_link = urlparse(link)
        filename = unquote(os.path.split(parsed_link.path)[1])
        photo_path = os.path.abspath(os.path.join(directory, filename))
        download_image(photo_path, link)


def fetch_nasa_images(directory, nasa_key):
    query_params = {
        'api_key': nasa_key,
        'count': '40'
    }
    url = 'https://api.nasa.gov/planetary/apod'
    headers = {
        'User-Agent': 'my-first-bot / 1.0'
    }
    response = requests.get(url, headers=headers, params=query_params)
    response.raise_for_status()

    images_descriptions = response.json()
    images_links = [image_description[key] for image_description in images_descriptions for key in image_description if
                    key == 'hdurl']

    for image_suffix, image_link in enumerate(images_links, start=1):
        filename = f'nasa_{image_suffix}{get_file_extension(image_link)}'
        path = os.path.abspath(os.path.join(directory, filename))
        download_image(path, image_link, query_params)


def fetch_nasa_epic_images(directory, nasa_key):
    query_params = {
        'api_key': nasa_key
    }
    url = 'https://api.nasa.gov/EPIC/api/natural'
    headers = {
        'User-Agent': 'my-first-bot / 1.0'
    }
    response = requests.get(url, headers=headers, params=query_params)
    response.raise_for_status()

    limit_response = response.json()[:10]

    for image_suffix, image_description in enumerate(limit_response, start=1):
        image_date = datetime.datetime.fromisoformat(image_description.get('date'))
        image_name = image_description.get('image')
        image_url = f'https://api.nasa.gov/EPIC/archive/natural/' \
                    f'{image_date.year}/{image_date.month:02}' \
                    f'/{image_date.day:02}/png/{image_name}.png'

        filename = f'nasa_epic_{image_suffix}.png'
        path = os.path.abspath(os.path.join(directory, filename))
        download_image(path, image_url, query_params)


def post_photo_to_telegram(bot, chat_id, photo_path, delay=24 * 60 * 60):
    with open(photo_path, mode='rb') as current_photo:
        bot.send_photo(chat_id, current_photo)
    time.sleep(delay)


def main():
    load_dotenv()
    directory = 'images'
    path_project = os.path.abspath('.')
    os.makedirs(os.path.join(path_project, directory), exist_ok=True)

    try:
        fetch_spacex_last_launch(directory)
        fetch_nasa_images(directory, nasa_key=os.getenv('NASA_KEY'))
        fetch_nasa_epic_images(directory, nasa_key=os.getenv('NASA_KEY'))

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

    chat_id = os.getenv('CHAT_ID')
    post_delay = int(os.getenv('POST_DELAY'))
    bot = ExtBot(token=os.getenv('TELEGRAM_KEY'))
    path = os.path.abspath(directory)
    for photo in os.listdir(path):
        photo_path = os.path.abspath(os.path.join(path, photo))
        try:
            post_photo_to_telegram(bot, chat_id, photo_path, post_delay)
        except error.BadRequest as e:
            print(e)


if __name__ == '__main__':
    main()
