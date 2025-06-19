# node:lts-slim
FROM node:22-slim
# https://github.com/Mermade/oas-kit/blob/main/packages/swagger2openapi/Dockerfile
LABEL maintainer="mike.ralphson@gmail.com" description="Swagger to OpenAPI"
ENV NODE_ENV=production

WORKDIR /usr/src/app

# install the app
RUN npm i -g swagger2openapi

CMD [ "swagger2openapi", "--help" ]