FROM nginx:alpine

# Copy built files to Nginx html directory
COPY ./frontend /usr/share/nginx/html

# Copy custom Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf
