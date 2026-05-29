FROM node:22-alpine

WORKDIR /app

COPY apps/web/package.json apps/web/
RUN cd apps/web && npm install

COPY apps/web/ apps/web/

WORKDIR /app/apps/web
RUN npm run build

CMD ["npm", "start"]
