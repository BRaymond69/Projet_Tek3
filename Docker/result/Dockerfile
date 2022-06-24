FROM node:12-alpine

RUN mkdir /app

COPY . /app

WORKDIR /app

RUN npm install --save /app

ENV PORT 80

EXPOSE 80

CMD ["node", "server.js"]