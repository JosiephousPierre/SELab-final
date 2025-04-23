-- Create the database
CREATE DATABASE IF NOT EXISTS labclass_db;
USE labclass_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'Student', 'Academic Coordinator', 'Lab InCharge', 'Faculty/Staff', 'System Administrator'
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    requires_approval BOOLEAN NOT NULL DEFAULT TRUE,
    date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL
);

-- Add system administrator account
INSERT INTO users (id, full_name, email, password, role, is_approved, requires_approval) 
VALUES ('admin', 'System Administrator', 'admin@uic.edu', '$2b$12$I42gD8WSUhcNyYDEhJKuaeVkTH/YmIYrK6j/TqwrC4RUaEIjLnzpy', 'System Administrator', TRUE, FALSE);
-- This password is 'admin123' hashed with bcrypt

-- Role-based permissions
CREATE TABLE IF NOT EXISTS role_permissions (
    role VARCHAR(50) PRIMARY KEY,
    permissions JSON NOT NULL
);

-- Insert default role permissions
INSERT INTO role_permissions (role, permissions) VALUES 
('Student', '{"view_schedule": true, "view_profile": true}'),
('Academic Coordinator', '{"view_schedule": true, "manage_schedule": true, "view_profile": true}'),
('Lab InCharge', '{"view_schedule": true, "view_lab_schedule": true, "view_profile": true}'),
('Faculty/Staff', '{"view_schedule": true, "view_profile": true}'),
('System Administrator', '{"view_schedule": true, "manage_schedule": true, "manage_users": true, "view_profile": true, "approve_users": true}');

-- User sessions table for authentication
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Audit log for tracking system events
CREATE TABLE IF NOT EXISTS audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36),
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Semesters table
CREATE TABLE IF NOT EXISTS semesters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample semesters
INSERT INTO semesters (name, is_active) VALUES 
('1st Sem 2025-2026', TRUE),
('2nd Sem 2025-2026', FALSE),
('Summer 2026', FALSE),
('1st Sem 2026-2027', FALSE),
('2nd Sem 2026-2027', FALSE),
('Summer 2027', FALSE);

-- Course offerings table
CREATE TABLE IF NOT EXISTS course_offerings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    year_and_section VARCHAR(50) NOT NULL,
    semester_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE CASCADE
);

-- Lab rooms
CREATE TABLE IF NOT EXISTS lab_rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    capacity INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert default lab rooms
INSERT INTO lab_rooms (name) VALUES
('L201'), ('L202'), ('L203'), ('L204'), ('L205'), ('IOT');

-- Instructors table
CREATE TABLE IF NOT EXISTS instructors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Insert sample instructors
INSERT INTO instructors (full_name) VALUES
('Dr. John Smith'),
('Prof. Maria Santos'),
('Engr. Robert Cruz'),
('Dr. Elizabeth Reyes'),
('Prof. Michael Johnson');

-- Schedules table
CREATE TABLE IF NOT EXISTS schedules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    semester_id INT NOT NULL,
    section VARCHAR(50) NOT NULL,
    course_code VARCHAR(50) NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    day VARCHAR(20) NOT NULL,
    second_day VARCHAR(20),
    lab_room_id INT NOT NULL,
    instructor_name VARCHAR(100) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    schedule_types JSON NOT NULL,
    status ENUM('draft', 'pending', 'approved') NOT NULL DEFAULT 'draft',
    class_type ENUM('lab', 'lec', 'lab/lec') NOT NULL,
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (semester_id) REFERENCES semesters(id),
    FOREIGN KEY (lab_room_id) REFERENCES lab_rooms(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create index for faster filtering
CREATE INDEX idx_schedules_semester ON schedules(semester_id);
CREATE INDEX idx_schedules_lab_room ON schedules(lab_room_id);

-- Password reset tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    token VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create index for faster token lookups
CREATE INDEX idx_password_reset_tokens ON password_reset_tokens(token);
CREATE INDEX idx_password_reset_user ON password_reset_tokens(user_id); 


-- Notifications table for centralized notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'info', 'success', 'alert', etc.
    related_to VARCHAR(50) NULL, -- What the notification is about (e.g., 'schedule')
    related_id INT NULL, -- ID of the related entity (e.g., semester_id)
    is_global BOOLEAN DEFAULT FALSE, -- Whether this notification should be sent to all users
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36) NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Junction table to track user-notification relationships
CREATE TABLE IF NOT EXISTS user_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    notification_id INT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    read_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (notification_id) REFERENCES notifications(id) ON DELETE CASCADE
);

-- Create indexes for faster querying
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
CREATE INDEX idx_notifications_related ON notifications(related_to, related_id);
CREATE INDEX idx_user_notifications_user ON user_notifications(user_id);
CREATE INDEX idx_user_notifications_read ON user_notifications(is_read);

-- Add table for tracking forced logouts
CREATE TABLE IF NOT EXISTS forced_logouts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;