# Student Performance Analytics API



## Project Overview

This project implements a RESTful API for managing and analysing student performance data.

The API allows users to store student information and explore how factors such as study hours, sleep, attendance, and socio-economic background influence exam performance.

**Key Features:**
- Full CRUD operations for student records
- CSV batch import with tracking
- Token-based authentication
- Score distribution analysis (per 10 points)
- Factor correlation analysis to identify most impactful factors on exam performance
- Filtering, searching and pagination

The project is developed using Django and Django REST Framework with an SQLite database.

**Live Demo:** https://heortappel.pythonanywhere.com


## Technology Stack

- Python
- Django
- Django REST Framework
- SQLite
- RESTful API


## Dataset
Data Source from kaggle
URL：https://www.kaggle.com/datasets/grandmaster07/student-exam-performance-dataset-analysis


## Setup & Installation

```bash
# Install dependencies
pip install django djangorestframework

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Import CSV data
python manage.py import_csv

# Start server
python manage.py runserver
```


## API Endpoints

Base URL:
- **Production:** `https://heortappel.pythonanywhere.com`
- **Local:** `http://127.0.0.1:8000`

### Student API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/students/ | List all students |
| POST | /api/students/ | Create a new student record |
| GET | /api/students/{id}/ | Get a student by ID |
| PUT | /api/students/{id}/ | Update a student (full) |
| PATCH | /api/students/{id}/ | Update a student (partial) |
| DELETE | /api/students/{id}/ | Delete a student |
| GET | /api/students/stats/ | Get statistics (overall, by gender, by school type) |
| POST | /api/students/upload_csv/ | Upload CSV file to import data |

### Batch API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/batches/ | List all import batches |
| GET | /api/batches/{id}/ | Get batch details |
| GET | /api/batches/{id}/students/ | Get all students in a batch |
| GET | /api/batches/{id}/stats/ | Get statistics for a batch |
| GET | /api/batches/{id}/analysis/ | Get score distribution and factor analysis |

**Analysis Response Example:**
```json
{
  "batch_number": 1,
  "total_students": 6607,
  "score_distribution": {
    "0-9": 0,
    "10-19": 0,
    "20-29": 0,
    "30-39": 0,
    "40-49": 0,
    "50-59": 831,
    "60-69": 2694,
    "70-79": 2029,
    "80-89": 879,
    "90-100": 174
  },
  "factor_correlations": {
    "hours_studied": 0.1631,
    "attendance": 0.1578,
    "tutoring_sessions": 0.1012,
    "sleep_hours": 0.0534,
    "physical_activity": 0.0198
  },
  "most_impactful_factor": {
    "name": "hours_studied",
    "correlation": 0.1631,
    "interpretation": "weak positive correlation"
  }
}
```

### Authentication API

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /api/register/ | Register new user | No |
| POST | /api/token/ | Get authentication token | No |

**Register:**
```
POST /api/register/
username=newuser&email=user@example.com&password=pass123456

Response: {"message": "User registered successfully", "username": "newuser", "token": "abc123..."}
```

**Get Token:**
```
POST /api/token/
username=testuser&password=testpass123

Response: {"token": "abc123..."}
```

**Use Token:**
```
curl -H "Authorization: Token abc123..." http://127.0.0.1:8000/api/students/
```

All other endpoints require authentication. Requests without a valid token will return:
```json
{"detail": "Authentication credentials were not provided."}
```


## Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| page | Page number | ?page=2 |
| gender | Filter by gender | ?gender=Male |
| school_type | Filter by school type | ?school_type=Public |
| min_score | Minimum exam score | ?min_score=70 |
| max_score | Maximum exam score | ?max_score=90 |
| search | Search text | ?search=High |
| ordering | Sort field (prefix - for desc) | ?ordering=-exam_score |


## CLI Commands

```bash
# Import CSV (creates new batch)
python manage.py import_csv

# Import specific file
python manage.py import_csv --file path/to/data.csv

# Clear all data and import
python manage.py import_csv --clear
```

