import os
from typing import Dict
from io import BytesIO

from dotenv import load_dotenv
from minio import Minio
from PIL import Image
from requests import get


def extract(dog_breed: str) -> Dict[str, str]:
    dog_images_url = {}

    api_url = f'https://imsea.herokuapp.com/api/1?q={dog_breed}'
    response = get(url=api_url)
    url_response = response.json()
    dog_images_url[dog_breed] = url_response['results'][::2]

    return dog_images_url

def load(dog: str, dog_images: dict) -> None:
    load_dotenv()

    client = Minio(
        endpoint='localhost:9000',
        secret_key=os.getenv('MINIO_SECRET_KEY'),
        access_key=os.getenv('MINIO_ACCESS_KEY')
    )

    image_count = 1

    for link in dog_images[dog]:
        response = get(url=link)
        img = Image.open(BytesIO(response.content))
        length = img.tell()
        img.seek(0)

        client.put_object(
            bucket_name='test_bucket', 
            object_name=f'{dog}_image_{image_count}',
            length=length,
            data=img
        )

        image_count += 1

def main() -> None:
    dog = 'Labrador Retriever'

    image_links = extract(dog)

    load(dog, image_links)

if __name__ == '__main__':
    main()
