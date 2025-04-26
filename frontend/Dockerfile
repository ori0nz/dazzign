FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy project files
COPY . .

# Build the app
RUN npm run build

# Install serve to run the built app
RUN npm install -g serve

# Expose the application port
EXPOSE 5173

# Command to run the application
CMD ["npm", "run", "dev", "--", "--host"] 