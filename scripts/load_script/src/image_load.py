import argparse
import os
import uuid
from argparse import Namespace
from datetime import datetime
from io import BytesIO
from typing import List

from minio import Minio
from requests import get


def parse_date(date: str) -> datetime:
    parsed_date = datetime.strptime(date, "%Y-%m-%d")

    return parsed_date


def cli() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('search_request', type=str, help='help')
    parser.add_argument('bucket', type=str, help='help')
    parser.add_argument('date', help='help', type=parse_date)
    list_of_arguments = parser.parse_args()

    return list_of_arguments


def get_links(search_request: str, date: datetime) -> List[str]:
    dog_images_url = {}

    api_url = f'https://imsea.herokuapp.com/api/1?q={search_request} {date}'
    response = get(url=api_url)
    url_response = response.json()
    dog_images_url = url_response['results'][::2]

    return dog_images_url


def load_in_bucket(list_of_urls: list, search_request: str, 
                   bucket_name: str, date: datetime) -> None:

    client = Minio(
        endpoint='host.docker.internal:9000',
        secret_key=os.getenv('MINIO_SECRET_KEY'),
        access_key=os.getenv('MINIO_ACCESS_KEY'),
        secure=False
    )

    for link in list_of_urls:
        response = get(url=link)
        unique_name = str(uuid.uuid4())
        img = BytesIO(response.content)
        size = len(response.content)
        img.seek(0)

        object_name = (
            f'year={date.year}/month={date.month}/day={date.day}/'
            f'{search_request}/{unique_name}'
        )

        client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=img,
            length=size
        )


def main() -> None: 
    args = cli()
    
    urls = get_links(args.search_request, args.date)
    
    load_in_bucket(
        list_of_urls=urls, 
        search_request=args.search_request, 
        bucket_name=args.bucket,
        date=args.date
    )


if __name__=='__main__':
    main()
