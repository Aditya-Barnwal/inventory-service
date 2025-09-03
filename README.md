# Inventory Service

This project is a standalone Inventory Service for an e-commerce platform, built with Spring Boot (Java), React, and MySQL. It provides RESTful APIs for inventory management and a modern frontend dashboard.

## Features
- Inventory CRUD (Create, Read, Update, Delete)
- Stock management
- OpenAPI (Swagger) documentation
- Dockerized for easy local development

## Tech Stack
- Backend: Spring Boot
- Frontend: React
- Database: MySQL
- DevOps: Docker, Docker Compose

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Java 17 (for manual backend build)
- Node.js (for manual frontend build)

### Local Development (Recommended)

1. Clone the repository:
   ```sh
   git clone <repo-url>
   cd inventory-service
   ```
2. Start all services:
   ```sh
   cd infra
   docker-compose up --build
   ```
3. Access the services:
   - Backend API: http://localhost:8080/api/v1/inventory
   - Swagger UI: http://localhost:8080/swagger-ui.html
   - Frontend: http://localhost:3000

### Manual Development

- **Backend:**
  - `cd backend`
  - `./mvnw spring-boot:run`
- **Frontend:**
  - `cd frontend`
  - `npm install && npm start`
- **MySQL:**
  - Use your local MySQL instance with the credentials in `backend/src/application.properties`

## Database Schema

The service will auto-create the `inventory_items` table:
- id (PK)
- name
- sku
- quantity
- location
- updated_at

## API Documentation

- Swagger UI: [http://localhost:8080/swagger-ui.html](http://localhost:8080/swagger-ui.html)

## License
MIT
