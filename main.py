from urllib.parse import urlparse
import requests
import os


def download_image(path, url):
    headers = {
        'User-Agent': 'my-first-bot / 1.0'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    with open(path, mode='wb') as file:
        file.write(response.content)


def fetch_spacex_last_launch(directory, url):
    headers = {
        'User-Agent': 'my-first-bot / 1.0'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
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

    for i, i_link in enumerate(images_links):
        print(i_link)
        parsed_link = urlparse(i_link)
        test_path = parsed_link.path
        start = test_path.rfind('/') + 1
        filename = parsed_link.path[start:]
        path = os.path.abspath(os.path.join(directory, filename))
        with open(path, mode='wb') as file:
            file.write(response.content)


def main():
    # filename = 'hubble.jpeg'
    # url_wiki = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg'
    url_spacex = 'https://api.spacexdata.com/v4/launches/'
    directory = 'images'
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)

    #     download_image(path, url_wiki)
        fetch_spacex_last_launch(directory, url_spacex)

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
