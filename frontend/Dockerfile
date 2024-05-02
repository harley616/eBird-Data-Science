# Use an official Node.js image as the base
FROM node:14-alpine as build

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Build the React app for production
RUN npm run build

ENV REACT_APP_BUILT = true
# Use Nginx as the base image to serve the app
FROM nginx:alpine

# Copy the build output from the previous stage to the NGINX html directory
COPY --from=build /app/build /usr/share/nginx/html

# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 3000
EXPOSE 80

# Start NGINX to serve the app
CMD ["nginx", "-g", "daemon off;"]
