FROM node:15

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install

COPY src/javascript .

EXPOSE 80

CMD [ "node", "server.js" ]