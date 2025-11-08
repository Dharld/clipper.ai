FROM node:20-bullseye-slim

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install --production=false

# Copy source
COPY . .

# Vite dev server listens on 5173 by default
EXPOSE 5173

# Start Vite dev server and bind to 0.0.0.0 so host can access it
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
