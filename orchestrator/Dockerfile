FROM node:20

# FROM alpine:latest
# RUN apk add --no-cache nodejs npm python3

WORKDIR /src
COPY . /src

RUN npm cache clean --force
RUN rm -rf node_modules package-lock.json

RUN npm install
RUN npm run build

ENTRYPOINT ["node", "/src/build/Index.js"]