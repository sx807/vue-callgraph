FROM node
WORKDIR /opt/vue
COPY package*.json ./
RUN npm cache clean -f && npm i
COPY . .
CMD ["npm","run","build:prod"]
