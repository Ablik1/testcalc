FROM node:20-alpine

WORKDIR /app
COPY package.json /app/package.json
COPY tsconfig.json /app/tsconfig.json
COPY vite.config.ts /app/vite.config.ts
COPY index.html /app/index.html
COPY public /app/public
RUN npm install
COPY src /app/src

EXPOSE 3000
CMD ["npm", "run", "dev"]
