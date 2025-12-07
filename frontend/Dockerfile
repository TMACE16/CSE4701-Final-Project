FROM node:18-alpine

WORKDIR /app

# Copy package files first (for caching)
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Run Vite dev server (accessible from host)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
