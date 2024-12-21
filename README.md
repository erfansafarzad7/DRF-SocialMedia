# Django Social Media Project

**This project is a sample social media platform built with Django, designed to demonstrate clean coding and advanced web development techniques.
The application showcases skills in integrating modern tools like `Django REST Framework`, `GraphQL`, `WebSocket`, and `Docker`.
It features core functionalities for `User Management`, `Real-Time Chat`, and `Post Interactions`, making it a comprehensive portfolio project.**

</br>

## Features

### General:
- Technologies Used:
  - Django REST Framework
  - GraphQL
  - WebSocket (Django Channels)
  - Celery, RabbitMQ, Redis
  - Docker, Nginx

### Functionalities:
1. User Management:
   - User list and profiles
   - OTP-based authentication
   - Follow/unfollow functionality
   - User notifications

2. Real-Time Chat:
   - Chat and Group managing system
   - Private messaging
   - Group chat
   - WebSocket support

3. Posts:
   - Create, update, and delete posts
   - Comments and reactions on posts
   - Tagging system for filtering posts by tags
   - GraphQL queries

### Security:
- Basic security measures implemented for general use. (Not configured for production-grade deployment.)


---
</br>

## Installation and Setup

1. Clone the repository:

```
  git clone https://github.com/erfansafarzad7/DRF-SocialMedia.git
  cd <project-folder>
```

2. Build and run Docker containers:
```
  docker-compose up --build
```

---
</br>

## Usage
- Import the provided Postman collection for testing the APIs.

---
</br>

# API Examples

### Get All Users:

**Request:**
```http
GET /api/auth/users/ HTTP/1.1
Host: 127.0.0.1:8000
```
**Response:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "User_1734715732",
            "user": "http://127.0.0.1:8000/api/auth/users/User_1734715732/",
            "is_online": false,
            "created_at": "2024-12-20"
        }
    ]
}
```

### Register New User:
**Note: first of all you nedd to send an otp-code to mobile number using this path:**

**Request for generate otp:**
```http
POST /api/auth/otp-request/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: multipart/form-data

mobile=1234567890
```
**Response:**
```json
{
    "message": "OTP sent successfully!"
}
```

**Then:**

**Request for confirm otp:**
```http
POST /api/auth/otp-verify/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: multipart/form-data

mobile=09000000000
otp=123456
password=12345678
```

**Response:**
```json
{
    "access": "your_access_token",
    "refresh": "your_refresh_token"
}
```

### Your Profile:

**Request:**
```http
GET /api/auth/profile/ HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer <your_access_token>
```
**Response:**
```json
{
    "id": 1,
    "username": "username",
    "mobile": "09000000000",
    "posts": [],
    "created_at": "2024-12-21"
}
```

---
</br>

## Future Enhancements
- Deployment of a live demo version.


## Contact Info
- LinkedIn: [https://www.linkedin.com/in/erfansafarzad7]
- Email: [erfansafarzad7@gmail.com]
- Telegram: [https://t.me/erfansafarzad7]
