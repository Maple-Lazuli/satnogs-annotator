FROM node:20-alpine3.17

COPY Inventory/src /opt/app/src

COPY Inventory/public /opt/app/public

COPY Inventory/package.json /opt/app/

COPY Inventory/package-lock.json /opt/app/


RUN PATH="$PATH"

WORKDIR /opt/app/

RUN npm install
EXPOSE 5173
CMD ["npm", "run", "dev","--","--host"]
