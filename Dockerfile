FROM nginx:alpine

# Install Python, pip, and build dependencies for uWSGI
RUN apk add --update python3 py3-pip \
    && apk add --virtual build-deps gcc python3-dev musl-dev linux-headers

# Install uWSGI
RUN pip3 install uwsgi

# Remove build dependencies to keep the image size small
RUN apk del build-deps

# Copy the content
COPY html /usr/share/nginx/html
COPY conf /etc/nginx/conf.d
COPY script.py /usr/share/nginx/
COPY uwsgi/uwsgi.ini /usr/share/nginx/
COPY name_dictionaries /usr/share/nginx/name_dictionaries

# Set the working dir
WORKDIR /usr/share/nginx

# Expose port 80
EXPOSE 80

# Start uWSGI and NGINX
CMD ["sh", "-c", "uwsgi --ini /usr/share/nginx/uwsgi.ini & nginx -g 'daemon off;'"]
