# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Docker (Recommended):**
```bash
make docker-up-build    # Build and run containers
make docker-migrate     # Run database migrations
make docker-superuser   # Create Django superuser
make docker-shell       # Open Django shell in container
make docker-down        # Stop and cleanup containers
```

**Local Development:**
```bash
make install           # Create venv and install dependencies
make migrate           # Apply database migrations
make makemigrations    # Create new migrations
make run              # Start dev server on 0.0.0.0:8000
make superuser        # Create Django superuser
make shell            # Open Django shell
```

**Testing:**
- No specific test commands are configured in Makefile
- Tests are located in `app/accounts/tests/` and `app/recruitment/tests.py`
- Run tests with: `python manage.py test` (from app/ directory)

## Architecture Overview

This is a Django 5.2.5 recruitment management system with role-based access control.

**Core Applications:**
- `accounts` - User authentication, profiles, and role management
- `recruitment` - Job postings, applications, scoring, and notifications

**User Roles (UserProfile.Roles):**
- `ADMIN` - Full system access
- `RECRUITER` - Can manage job postings and review applications
- `CANDIDATE` - Can view jobs and submit applications

**Key Models:**
- `accounts.UserProfile` - Extends Django User with role-based permissions
- `recruitment.Poste` - Job postings
- `recruitment.Candidature` - Job applications with file uploads
- `recruitment.Score` - AI-generated application scores
- `recruitment.Notification` - System notifications

## API Structure

REST API available at `/recruitment/api/`:
- `/postes/` - Job postings CRUD (Recruiter/Admin only for CUD)
- `/candidatures/` - Applications management (role-based access)
- `/scores/` - Application scoring (read-only for candidates)

Authentication: Session-based (DRF SessionAuthentication + BasicAuthentication)

## File Structure

```
app/                    # Django project root (manage.py here)
├── app/               # Main Django settings
├── accounts/          # Authentication & user management
├── recruitment/       # Core recruitment functionality
├── db.sqlite3        # Development database
└── media/            # User-uploaded files (CVs, cover letters)
```

**File Uploads:**
- CVs: `media/cvs/{user_id}/{filename}`
- Cover letters: `media/lettres/{user_id}/{filename}`
- Validated file types in `recruitment.validators`

## Development Notes

- French language (LANGUAGE_CODE = 'fr-FR')
- Email backend configured (console in DEBUG mode, SMTP in production)
- File permissions: 0o644 for files, 0o755 for directories
- SQLite database with proper indexing on commonly queried fields
- Security headers configured (X-Frame-Options, CSRF protection)