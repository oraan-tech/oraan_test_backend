# Invoice Refactoring Exercise

A Django-based invoice generation system for interview candidates to refactor and improve.

## Project Structure

```
invoice_refactor/
├── manage.py
├── requirements.txt
├── invoice_refactor/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── customers/                 # Customer and subscription models
│   ├── models.py
│   └── fixtures/
│       └── seed.json         # Sample data
└── invoices/                  # Invoice models and API
    ├── models.py
    ├── views.py              # Invoice generation endpoint
    └── urls.py
```

## Setup Instructions

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Load fixture data**:
   ```bash
   python manage.py loaddata customers/fixtures/seed.json
   ```

5. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

6. **Test the endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/invoices/generate/ \
     -H "Content-Type: application/json" \
     -d '{"customer_id": "CUST001"}'
   ```

## Reset Database

To reset the database back to its initial state:

```bash
rm db.sqlite3
python manage.py migrate
python manage.py loaddata customers/fixtures/seed.json
```

## Task

Review the codebase and refactor the invoice generation system to follow Django best practices. Consider code quality, performance, architecture, and maintainability.

## Test Data

The seed data includes:
- 5 customers (CUST001 - CUST005)
- 10 subscriptions in various states
- 3 existing invoices
