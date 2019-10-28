FROM python:3.7-buster
LABEL maintainer="knr@purdue.edu"

COPY . /code/

RUN pip install --upgrade pip
RUN pip install -r /code/requirements.txt

EXPOSE 8000

CMD python -m code
