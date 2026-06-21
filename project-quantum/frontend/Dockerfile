# Use official Nginx light alpine base image
FROM nginx:alpine

# Remove default Nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy frontend static files into Nginx default serving directory
COPY index.html style.css script.js /usr/share/nginx/html/
COPY pages/ /usr/share/nginx/html/pages/

# Expose Nginx default HTTP port
EXPOSE 80

# Start Nginx in the foreground to keep the container active
CMD ["nginx", "-g", "daemon off;"]
