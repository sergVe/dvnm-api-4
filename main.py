from urllib.parse import urlparse, urlsplit, unquote
import requests
import os
import datetime
from dotenv import load_dotenv


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
        print(i_link)
        parsed_link = urlparse(i_link)
        test_path = parsed_link.path
        start = test_path.rfind('/') + 1
        filename = parsed_link.path[start:]
        path = os.path.abspath(os.path.join(directory, filename))
        download_image(path, i_link)


def fetch_nasa_images(directory, url):
    query_params = {
        'api_key': os.getenv('NASA_KEY'),
        'count': '50'
    }
    response = get_response(url, query_params)
    data = response.json()
    images_links = [data_unit[key] for data_unit in data for key in data_unit if key == 'hdurl']
    for i, i_link in enumerate(images_links):
        filename = f'nasa_{i + 1}{get_file_extension(i_link)}'
        path = os.path.abspath(os.path.join(directory, filename))
        download_image(path, i_link)


def fetch_nasa_epic_images(directory, url):
    image_date, image_name, image_url = '', '', ''
    query_params = {
        'api_key': os.getenv('NASA_KEY'),
        'count': '9'
    }
    response = get_response(url, query_params)
    for i, response_unit in enumerate(response.json()):
        print(i + 1)
        for k, v in response_unit.items():
            print(k, v)
            if k == 'date':
                image_date = datetime.datetime.fromisoformat(v)
                print(image_date)
            if k == 'image':
                image_name = v
        image_url = f'https://api.nasa.gov/EPIC/archive/natural/' \
                    f'{image_date.year}/{image_date.month}/{image_date.day}' \
                    f'/png/{image_name}.png'

        filename = f'nasa_epic_{i + 1}.png'
        path = os.path.abspath(os.path.join(directory, filename))
        params = {k: v for (k, v) in query_params.items() if k == 'api_key'}
        print(params)
        download_image(path, image_url, params)
        print('=' * 8)


def main():
    # filename = 'hubble.jpeg'
    # url_wiki = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg'
    url_spacex = 'https://api.spacexdata.com/v4/launches/'
    directory = 'images'
    nasa_directory = 'nasa_directory'
    nasa_epic_directory = 'nasa_epic_directory'
    nasa_url = 'https://api.nasa.gov/planetary/apod'
    nasa_epic_url = 'https://api.nasa.gov/EPIC/api/natural'
    test_nasa_epic_image_url = 'https://api.nasa.gov/EPIC/archive/natural/2021/12/15/png/epic_1b_20211215001751.png?api_key=xhQ4MBfxmfhUsxakRU2rZqZrdIannJ5se0YJzUEl'

    try:
        load_dotenv()
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(nasa_directory):
            os.makedirs(nasa_directory)
        if not os.path.exists(nasa_epic_directory):
            os.makedirs(nasa_epic_directory)

        # fetch_nasa_images(nasa_directory, nasa_url)
        # fetch_nasa_images(nasa_directory, nasa_url)
        fetch_nasa_epic_images(nasa_epic_directory, nasa_epic_url)

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

# xhQ4MBfxmfhUsxakRU2rZqZrdIannJ5se0YJzUEl
# https://api.nasa.gov/planetary/apod?api_key=xhQ4MBfxmfhUsxakRU2rZqZrdIannJ5se0YJzUEl
