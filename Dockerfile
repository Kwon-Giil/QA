FROM nginx:alpine
RUN echo "<h1>Hello, Custom Dockerfile!</h1>" > /usr/share/nginx/html/index.html