FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

CMD ["streamlit", "run", "/code/app.py", "--server.address", "0.0.0.0", "--server.port", "7860",
 "--server.enableWebsocketCompression", "True", ]


RUN mkdir /.cache
RUN chmod 777 /.cache
RUN mkdir .chroma
RUN chmod 777 .chroma