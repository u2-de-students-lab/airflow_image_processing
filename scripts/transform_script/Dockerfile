FROM python:3
ARG APP_NAME=image_transformation
RUN python -m pip install --upgrade pip
RUN mkdir /root/${APP_NAME}
WORKDIR /root/${APP_NAME}

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./src/transform.py/ .
ENTRYPOINT [ "python3", "transform.py" ]
