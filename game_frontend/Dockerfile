FROM node:13-alpine
LABEL maintainer="knr@purdue.edu"

COPY . /code
WORKDIR /code/

RUN yarn install

EXPOSE 8080

CMD yarn serve
