# Student Performance Analytics API

A Django REST Framework API for tracking and analyzing student academic performance — including courses, enrollments, grades, and aggregate analytics.

---

## Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Apply database migrations

```bash
python manage.py makemigrations analytics
python manage.py migrate
```

### 3. (Optional) Create a superuser for the admin panel

```bash
python manage.py createsuperuser
```

### 4. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

---

## Running Tests

```bash
python manage.py test analytics --verbosity=2
```

---

## API Endpoints

### Students

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students/` | List all students (paginated, searchable) |
| POST | `/api/students/` | Create a new student |
| GET | `/api/students/{id}/` | Retrieve a student |
| PUT/PATCH | `/api/students/{id}/` | Update a student |
| DELETE | `/api/students/{id}/` | Delete a student |
| GET | `/api/students/{id}/performance/` | Student's per-course average and overall GPA |

**Query parameters:** `search` (first_name, last_name, email, student_id), `ordering` (enrollment_date, last_name)

---

### Courses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/courses/` | List all courses |
| POST | `/api/courses/` | Create a new course |
| GET | `/api/courses/{id}/` | Retrieve a course |
| PUT/PATCH | `/api/courses/{id}/` | Update a course |
| DELETE | `/api/courses/{id}/` | Delete a course |
| GET | `/api/courses/{id}/statistics/` | Enrolled count, average score, grade distribution |

**Query parameters:** `search` (name, code, instructor)

---

### Enrollments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/enrollments/` | List all enrollments |
| POST | `/api/enrollments/` | Enroll a student in a course |
| GET | `/api/enrollments/{id}/` | Retrieve an enrollment |
| PUT/PATCH | `/api/enrollments/{id}/` | Update enrollment status |
| DELETE | `/api/enrollments/{id}/` | Remove an enrollment |

**Query parameters:** `student`, `course`, `status` (ACTIVE / COMPLETED / DROPPED)

---

### Grades

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/grades/` | List all grades |
| POST | `/api/grades/` | Record a grade |
| GET | `/api/grades/{id}/` | Retrieve a grade |
| PUT/PATCH | `/api/grades/{id}/` | Update a grade |
| DELETE | `/api/grades/{id}/` | Delete a grade |

**Query parameters:** `enrollment`

> Grade letters are computed automatically: A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, F < 60.

---

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/summary/` | Total students, courses, enrollments, and overall average score |
| GET | `/api/analytics/top-performers/` | Top 10 students ranked by GPA |
| GET | `/api/analytics/course-performance/` | All courses with their average score and enrollment count |

---

## Project Structure

```
student_analytics/   # Django project package (settings, root URLs, WSGI)
analytics/           # Main app — models, serializers, views, tests, admin
manage.py
requirements.txt
```

## Tech Stack

- **Python 3** / **Django 4.2**
- **Django REST Framework 3.14+**
- **django-filter** for field-level filtering
- **SQLite** (default development database)
CW1
