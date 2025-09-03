# ---------- Build Stage ----------
    FROM node:18-alpine AS build
    WORKDIR /app
    
    # Install dependencies (using npm or yarn)
    COPY package.json package-lock.json ./
    RUN npm install
    
    # Copy rest of the source and build
    COPY . .
    RUN npm run build
    
    # ---------- Runtime Stage ----------
    FROM nginx:alpine
    WORKDIR /usr/share/nginx/html
    
    # Copy build output to Nginx html folder
    COPY --from=build /app/build ./
    
    # Copy a default nginx config (optional tweak)
    COPY nginx.conf /etc/nginx/conf.d/default.conf
    
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]
    