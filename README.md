# Academic Management System – Alternova Technical Test

This repository contains the backend implementation of an academic management system for universities.

The solution has been developed with **Python 3.10**, **Django 4.2**, **Django REST Framework** & **PostgreSQL**, and is fully **dockerized** for easy deployment and testing.

---

## Implemented functionalities

| Module                          | Description                                                                                           | Estado |
| ------------------------------- | ----------------------------------------------------------------------------------------------------- | ------ |
| **Autenticación JWT**           | Log in by email or username. Use RS256-signed access and refresh tokens.                              | OK      |
| **Gestión de usuarios**         | CRUD for `admin`, `teacher` and `student` users, with creation controlled from admin.                 | OK      |
| **Asignaturas e Inscripciones** | Adding and modifying courses; student registration, credit validation, and prerequisites.             | OK      |
| **Calificaciones**              | Teacher assigns grade (0–5); enrollment status updates to `completed`.                                | OK      |
| **GPA**                         | Calculation of the weighted average according to the credits of the subjects taken.                   | OK      |
| **Listado & Historial**         | Endpoints to list students and view their complete academic history.                                  | OK      |
| **Seguridad**                   | Authentication, role-based permissions, strict business validations.                                  | OK      |
| **Testing**                     | Integrated testing with `pytest` and `model_bakery`; current coverage exceeds **75%**.                | OK      |
| **Docker**                      | Services `app`, `db`, `celery`, `beat` defined in `docker-compose`.                                   | OK      |
| **Notificaciones**              | Signal system ready. Final integration via email channel is pending.                                  | OK     |
| **Reportes PDF**                | Basic report export to PDF. Encryption integration pending.                                           | OK     |

---

## Local installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

### Test:

```bash
pytest --cov=. --cov-report=term-missing
```

---

## Environment Configuration

- Variables de entorno en `.env`:
  - `SECRET_KEY`
  - `DATABASE_URL`
  - `ALLOWED_HOSTS`
  - `JWT_PUBLIC_KEY` y `JWT_PRIVATE_KEY`
  - `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, etc. (para notificaciones futuras)

---

## Environment Configuration

The system follows an architecture based on decoupled services and asynchronous tasks using Celery. SOLID principles, DRY patterns, and view- and model-level validation are applied.

Middleware for auditing and decorators for critical business logic such as role validation or prerequisites are implemented.


---

## Docker Compose

```bash
docker-compose up --build
```

| Service    | Port   | Description                       |
| ---------- | ------ | --------------------------------- |
| **app**    | 8000   | API Django REST Framework         |
| **db**     | 5432   | PostgreSQL                        |
| **celery** | -      | Asynchronous Task Worker          |
| **beat**   | -      | Periodic Task Planner             |

---

## Security

- Stateless JWT Authentication (stateless)
- Request audit middleware
- Business validation with decorators according to role
- Using select_related and prefetch_related for optimization
- Passwords stored with PBKDF2

---

## API Documentation

Accessible via browser:

```
http://localhost:8000/api/docs/
```

Includes:

- JWT Authentication
- User endpoints
- Course endpoints, enrollment, GPA, history
- Expected errors and responses by HTTP code

---

## License

This project is distributed under the MIT license.

---

For more details, contact the development team or check out the configuration and automated test files.

