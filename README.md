# Student Performance Analytics API



## Project Overview

This project implements a RESTful API for managing and analysing student performance data.

The API allows users to store student information and explore how factors such as study hours, sleep, attendance, and socio-economic background influence exam performance.

The project is developed using Django and Django REST Framework with an SQLite database.


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

Base URL: `http://127.0.0.1:8000`

### Student API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/students/ | List all students (paginated) |
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

