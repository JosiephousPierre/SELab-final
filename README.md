# Lab Class Management System

A comprehensive web application for managing laboratory class schedules and user accounts.

## Features

- User authentication with role-based access control
- Automatic approval for student accounts
- Admin approval workflow for faculty and staff accounts
- Schedule management for academic coordinators
- Calendar views for lab schedules

## Database Setup

1. Create the MySQL database using the provided schema:

```bash
mysql -u root -p < db_schema.sql
```

2. This will create:
   - The `labclass_db` database
   - User accounts table
   - Role permissions table
   - User sessions table
   - Audit log table
   - Default admin user (username: admin, password: admin123)

## Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Start the FastAPI backend:

```bash
python main.py
```

The API will be available at http://localhost:8000

## Frontend Setup

1. Install the required Node.js packages:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## Usage

1. **Sign Up**: Users can sign up with different roles:
   - Students are automatically approved
   - Other roles (Academic Coordinator, Lab InCharge, Faculty/Staff) require admin approval

2. **Login**:
   - Use the credentials you created during signup
   - For admin access, use the default admin account

3. **Account Management** (Admin only):
   - Navigate to Account Management to see pending accounts
   - Approve or reject user account requests

## Technical Stack

- **Frontend**: Vue.js with Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: MySQL 