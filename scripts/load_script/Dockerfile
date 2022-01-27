FROM python:3
ARG APP_NAME=image_load
RUN python -m pip install --upgrade pip
RUN mkdir /root/${APP_NAME}
WORKDIR /root/${APP_NAME}

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./src/image_load.py/ .
ENTRYPOINT [ "python3", "image_load.py" ]
