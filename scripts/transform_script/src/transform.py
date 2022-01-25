import argparse
import os
from argparse import Namespace
from datetime import datetime
from io import BytesIO
from PIL import Image
from typing import List

from minio import Minio


def parse_date(date: str) -> datetime:
    parsed_date = datetime.strptime(date, "%Y-%m-%d")

    return parsed_date


def cli() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('search_request', type=str, 
                        help='Image that you want to search')
    parser.add_argument('source_bucket_name', type=str, 
                        help='Name of the bucket with raw images')
    parser.add_argument('load_bucket_name', type=str, 
                        help='Bucket name for transformed images')
    parser.add_argument('date', type=parse_date, help='Search date')
    parser.add_argument('width', type=int, help='New image width')
    parser.add_argument('height', type=int, help='New image height')

    arguments = parser.parse_args()

    return arguments


def take_images_from_bucket(search_request: str, source_bucket: str, 
                            date: datetime, client: Minio) -> List[str]:
    objects = []
    prefix = (
        f'year={date.year}/month={date.month}/'
        f'day={date.day}/{search_request}/'
    )

    for obj in client.list_objects(bucket_name=source_bucket, prefix=prefix):
        objects.append(obj.object_name)

    return objects


def resize_image(client: Minio, bucket_object: str,
                 source_bucket: str, 
                 width: int, height: int) -> BytesIO:
    try:
        file = client.get_object(source_bucket, bucket_object)
        bytes_io_file = BytesIO(file.read())
    finally:
        file.close()
        file.release_conn()
    image = Image.open(bytes_io_file)
    new_image = image.resize((width, height))
    byte_io = BytesIO()
    new_image.save(byte_io, 'jpeg')

    return byte_io


def load_to_bucket(objects: List[str], client: Minio, 
                   search_request: str, source_bucket: str,
                   processed_bucket: str, date: datetime, width: int, 
                   height: int) -> None:

    for obj in objects:
        image = resize_image(
            client=client,
            source_bucket=source_bucket,
            bucket_object=obj, 
            width=width, 
            height=height
        )

        length = image.getbuffer().nbytes
        image.seek(0)

        name_split = obj.split('/')

        object_name = (
            f'year={date.year}/month={date.month}/day={date.day}/'
            f'{search_request}/{width}x{height}/{name_split[-1]}'
        )
    
        client.put_object(
            bucket_name=processed_bucket,
            object_name=object_name,
            data=image,
            length=length
        )


def main():
    client = Minio(
        endpoint='127.0.0.1:9000',
        # endpoint='host.docker.internal:9000',
        # secret_key=os.getenv('MINIO_SECRET_KEY'),
        # access_key=os.getenv('MINIO_ACCESS_KEY'),
        secret_key='testsecretkey',
        access_key='testaccesskey',
        secure=False
    )

    args = cli()

    objects = take_images_from_bucket(
        search_request=args.search_request, 
        source_bucket=args.source_bucket_name,
        date=args.date,
        client=client
    )

    load_to_bucket(
        objects=objects,
        client=client,
        search_request=args.search_request,
        source_bucket=args.source_bucket_name,
        processed_bucket=args.load_bucket_name,
        date=args.date,
        width=args.width,
        height=args.height
    )
    

if __name__ == '__main__':
    main()
