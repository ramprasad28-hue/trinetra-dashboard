# 🛡️ TRINETRA - Network Security Scanner

A production-ready Django cybersecurity dashboard for network scanning and vulnerability analysis.

## ✨ Features

- ✅ User authentication (signup/login)
- ✅ Network port scanning with Nmap
- ✅ Real-time risk analysis
- ✅ Scan history with pagination
- ✅ User profiles with statistics
- ✅ Beautiful Bootstrap 5 UI
- ✅ Database optimization with indexing
- ✅ Comprehensive error handling
- ✅ Logging system
- ✅ Admin interface

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
# Copy environment file
cp .env.example .env

# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Edit .env and paste the SECRET_KEY
nano .env
```

### 3. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 5. Run Development Server

```bash
python manage.py runserver
```

### 6. Access the Application

- **Main App:** http://localhost:8000/login/
- **Admin Dashboard:** http://localhost:8000/admin/

## 📦 Project Structure

```
trinetra/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env                      # Environment config (create from .env.example)
├── .env.example              # Environment template
├── db.sqlite3                # SQLite database (auto-created)
│
├── trinetra/                 # Main project package
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py
│   └── asgi.py
│
├── scanner/                  # Scanner app
│   ├── migrations/           # Database migrations
│   ├── templates/            # HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── scan.html
│   │   ├── result.html
│   │   ├── history.html
│   │   ├── profile.html
│   │   └── scan_detail.html
│   │
│   ├── __init__.py
│   ├── admin.py             # Admin interface
│   ├── apps.py
│   ├── forms.py             # Form validation
│   ├── models.py            # Database models
│   ├── urls.py              # App URL routing
│   ├── utils.py             # Utility functions
│   ├── views.py             # View logic
│   └── tests.py             # Unit tests
│
├── static/                   # Static files (CSS, JS, images)
├── media/                    # User uploads
├── logs/                     # Application logs
└── .gitignore               # Git ignore rules
```

## 🔧 Configuration

### Database

Default uses SQLite. To switch to PostgreSQL:

Edit `.env`:
```ini
DB_ENGINE=django.db.backends.postgresql
DB_NAME=trinetra_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Email (Optional - for password reset)

Edit `.env`:
```ini
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

## 🔐 Security

- Environment-based configuration
- HTTPS/SSL ready
- CSRF protection
- Password validation (min 8 chars)
- Input sanitization
- SQL injection prevention (Django ORM)
- XSS prevention (template escaping)
- Error handling with logging

## 📊 Models

### ScanResult
- Stores network scan results
- Tracks scan status and timing
- Parses and stores results in JSON
- Calculates risk level

### UserScanStatistics
- Tracks user scanning metrics
- Total scans and open ports
- Average scan time

### PortService
- Common port mappings
- Service identification

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific test
python manage.py test scanner.tests.AuthenticationTests
```

## 📝 Admin Interface

Visit `/admin/` with your superuser account to:
- Manage scans
- View user statistics
- Configure port services
- Track scan history

## 🚀 Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn trinetra.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "trinetra.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Recommended Platforms

- Render (render.com)
- Railway (railway.app)
- Heroku
- DigitalOcean
- AWS EC2

## 🔍 Usage

### 1. Create Account
- Go to `/signup/`
- Fill in username, email, password
- Click "Create Account"

### 2. Login
- Go to `/login/`
- Enter credentials
- Click "Login"

### 3. Perform Scan
- Enter target IP, domain, or CIDR range
- Select port range (default: 1-1024)
- Click "Start Scan"
- View results with risk analysis

### 4. View History
- Go to "History" tab
- Filter by status or target
- Click on a scan to view details
- Delete scans you no longer need

### 5. Check Profile
- Go to "Profile" tab
- View statistics
- See recent scans

## 📖 API Documentation

### Forms

#### TrintraUserCreationForm
- Username validation (3+ chars, alphanumeric + underscore)
- Email validation (unique, valid format)
- Password confirmation
- Password strength validation

#### TrintraLoginForm
- Username and password validation
- Error handling

#### TrinetraScanForm
- Target validation (IPv4, domain, CIDR)
- Port range validation
- Scan type selection

### Views

#### scan_view
- GET: Display scan form
- POST: Perform scan, store results

#### history_view
- Display paginated scan history (10 per page)
- Filter by status and target

#### profile_view
- Display user statistics
- Show recent scans

#### scan_detail_view
- Display detailed scan results
- Show risk analysis

#### delete_scan_view
- Delete specific scan

## 🐛 Troubleshooting

### Error: ModuleNotFoundError: No module named 'scanner.forms'
```bash
# Make sure scanner/forms.py exists
ls scanner/forms.py
```

### Error: No such table: scanner_scanresult
```bash
# Run migrations
python manage.py migrate
```

### Error: TemplateDoesNotExist: base.html
```bash
# Make sure templates directory exists
mkdir -p scanner/templates
# Copy templates to scanner/templates/
```

### Nmap not found
```bash
# Linux/Mac
sudo apt-get install nmap
brew install nmap

# Windows
# Download from https://nmap.org/download
```

## 📚 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Nmap Documentation](https://nmap.org/docs.html)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)

## 📄 License

This project is for educational purposes.

## ⚖️ Legal Notice

**IMPORTANT:** Only scan networks you own or have explicit written permission to test. Unauthorized network scanning is illegal.

## 👥 Author

Created as a portfolio project demonstrating full-stack Django development.

## 🙏 Acknowledgments

- Django framework
- Nmap community
- Bootstrap team
- Python community

---

**Version:** 2.0 (Production-Ready)  
**Status:** Active Development ✅  
**Last Updated:** 2024
