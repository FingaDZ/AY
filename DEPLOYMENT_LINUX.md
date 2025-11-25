# AY HR Management - Linux Deployment Guide

## System Requirements

- **OS**: Ubuntu 22.04 LTS (or compatible)
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk**: 10GB free space
- **Network**: Static IP configuration recommended
- **Access**: Root or sudo privileges

## Prerequisites

### 1. System Update
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Packages
```bash
# Essential tools
sudo apt install -y git curl wget build-essential

# Python 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# MariaDB Server
sudo apt install -y mariadb-server mariadb-client
sudo systemctl enable mariadb
sudo systemctl start mariadb
```

## Database Setup

### 1. Secure MariaDB Installation
```bash
sudo mysql_secure_installation
# Set root password: !Yara@2014 (or your preferred password)
# Remove anonymous users: Y
# Disallow root login remotely: N (if you need remote access)
# Remove test database: Y
# Reload privilege tables: Y
```

### 2. Create Database and User
```bash
sudo mysql -uroot -p
```

```sql
-- Create database
CREATE DATABASE ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (replace password if needed)
CREATE USER 'ayhr_user'@'localhost' IDENTIFIED BY '!Yara@2014';
GRANT ALL PRIVILEGES ON ay_hr.* TO 'ayhr_user'@'localhost';
FLUSH PRIVILEGES;

-- Exit
EXIT;
```

### 3. Import Database Schema
```bash
# If you have the SQL file
mysql -uayhr_user -p'!Yara@2014' ay_hr < database/create_database.sql

# Or restore from production dump
mysqldump -h<PROD_SERVER_IP> -un8n -p'!Yara@2014' ay_hr | mysql -uayhr_user -p'!Yara@2014' ay_hr
```

## Installation Automatisée (Recommandée)

### 1. Télécharger et Installer
```bash
# Cloner le dépôt
git clone https://github.com/FingaDZ/AY.git /opt/ay-hr
cd /opt/ay-hr

# Rendre le script exécutable
chmod +x install.sh

# Lancer l'installation
sudo ./install.sh
```

Le script va automatiquement :
- Installer les dépendances (Python, Node.js, MariaDB)
- Configurer la base de données
- Installer l'application
- Configurer et démarrer les services

### 2. Mise à Jour
Pour mettre à jour l'application vers la dernière version :

```bash
cd /opt/ay-hr
sudo ./update.sh
```

## Installation Manuelle (Avancée)

### 1. Create Application Directory
```bash
sudo mkdir -p /opt/ay-hr
sudo chown $USER:$USER /opt/ay-hr
cd /opt/ay-hr
```

### 2. Transfer Application Files
**Option A: From Git Repository**
```bash
git clone https://github.com/FingaDZ/AY.git /opt/ay-hr
```

**Option B: Manual Transfer (WinSCP/SCP)**
```bash
# From Windows machine:
scp -r "f:\Code\AY HR\backend" root@<SERVER_IP>:/opt/ay-hr/
scp -r "f:\Code\AY HR\frontend" root@<SERVER_IP>:/opt/ay-hr/
scp "f:\Code\AY HR\irg.xlsx" root@<SERVER_IP>:/opt/ay-hr/
```

### 3. Backend Setup

#### Create Python Virtual Environment
```bash
cd /opt/ay-hr/backend
python3.11 -m venv .venv
source .venv/bin/activate
```

#### Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**IMPORTANT**: If you encounter bcrypt/passlib compatibility issues:
```bash
pip install 'bcrypt<4.0.0' --force-reinstall
```

#### Configure Backend Environment
```bash
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=mysql+pymysql://ayhr_user:%21Yara%402014@localhost/ay_hr

# Security
SECRET_KEY=your-secret-key-change-this-in-production

# CORS (adjust for your domain)
CORS_ORIGINS=http://localhost:3000,http://192.168.20.53:3000

# Application
APP_NAME=AY HR Management
DEBUG=False
EOF
```

**CRITICAL**: URL-encode special characters in password:
- `!` becomes `%21`
- `@` becomes `%40`

### 4. Frontend Setup

#### Install Node Dependencies
```bash
cd /opt/ay-hr/frontend
npm install
```

#### Build Frontend
```bash
npm run build
```

#### Fix Vite Permissions (if needed)
```bash
chmod +x node_modules/.bin/vite
```

### 5. Create IRG Tax File
Ensure the `irg.xlsx` file is present at `/opt/ay-hr/irg.xlsx`. This file contains the tax calculation tables.

## System Services Configuration

### 1. Backend Service

Create service file:
```bash
sudo nano /etc/systemd/system/ayhr-backend.service
```

Content:
```ini
[Unit]
Description=AY HR Management - Backend API
After=network.target mariadb.service
Wants=mariadb.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ay-hr/backend
Environment="PATH=/opt/ay-hr/backend/.venv/bin"
ExecStart=/opt/ay-hr/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 2. Frontend Service

Create service file:
```bash
sudo nano /etc/systemd/system/ayhr-frontend.service
```

Content:
```ini
[Unit]
Description=AY HR Management - Frontend
After=network.target ayhr-backend.service
Wants=ayhr-backend.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ay-hr/frontend
ExecStart=/usr/bin/npm run preview -- --host 0.0.0.0 --port 3000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 3. Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable ayhr-backend
sudo systemctl enable ayhr-frontend

# Start services
sudo systemctl start ayhr-backend
sudo systemctl start ayhr-frontend

# Check status
sudo systemctl status ayhr-backend
sudo systemctl status ayhr-frontend
```

## Common Issues and Solutions

### Issue 1: Database Connection Error
**Symptom**: Backend fails with `OperationalError: (2003, "Can't connect to MySQL")`

**Solution**:
- Verify MariaDB is running: `sudo systemctl status mariadb`
- Check DATABASE_URL has URL-encoded password
- Test connection: `mysql -uayhr_user -p'!Yara@2014' ay_hr -e "SHOW TABLES;"`

### Issue 2: bcrypt Password Hashing Error
**Symptom**: `ValueError: password cannot be longer than 72 bytes`

**Solution**:
```bash
cd /opt/ay-hr/backend
source .venv/bin/activate
pip install 'bcrypt<4.0.0' --force-reinstall
sudo systemctl restart ayhr-backend
```

### Issue 3: User Schema Mismatch
**Symptom**: `AttributeError: 'User' object has no attribute 'username'` or similar

**Solution**: Ensure your User model matches the database schema:
- Production uses: `email`, `nom`, `prenom`, `password_hash`, `role`, `actif`, `date_creation`, `derniere_connexion`
- NOT: `username`, `hashed_password`, `created_at`, `updated_at`

### Issue 4: 500 Error on API Endpoints
**Symptom**: All GET requests return 500 errors

**Check logs**:
```bash
journalctl -u ayhr-backend -n 50 --no-pager
```

**Common causes**:
- Model/schema mismatch between code and database
- Missing database columns
- Wrong column names in queries

### Issue 5: IRG File Not Found
**Symptom**: `FileNotFoundError: Fichier IRG requis non trouvé: /opt/ay-hr/irg.xlsx`

**Solution**:
```bash
# Copy from production or local
scp "f:\Code\AY HR\irg.xlsx" root@<SERVER_IP>:/opt/ay-hr/
# Verify
ls -lh /opt/ay-hr/irg.xlsx
```

### Issue 6: PDF Generation Shows Hardcoded Values
**Symptom**: Payslips show "Entreprise" or "N/A" instead of database values

**Solution**: Ensure PDFGenerator receives database session:
```python
# Correct:
pdf_generator = PDFGenerator(db=db)

# Wrong:
pdf_generator = PDFGenerator()
```

### Issue 7: Frontend Permission Denied
**Symptom**: Service fails with `EACCES: permission denied` when starting Vite

**Solution**:
```bash
cd /opt/ay-hr/frontend
chmod +x node_modules/.bin/vite
sudo systemctl restart ayhr-frontend
```

## Service Management Commands

```bash
# Start services
sudo systemctl start ayhr-backend
sudo systemctl start ayhr-frontend

# Stop services
sudo systemctl stop ayhr-backend
sudo systemctl stop ayhr-frontend

# Restart services
sudo systemctl restart ayhr-backend
sudo systemctl restart ayhr-frontend

# Check status
sudo systemctl status ayhr-backend
sudo systemctl status ayhr-frontend

# View logs (live)
journalctl -u ayhr-backend -f
journalctl -u ayhr-frontend -f

# View recent logs
journalctl -u ayhr-backend -n 100 --no-pager
```

## Accessing the Application

- **Frontend**: `http://<SERVER_IP>:3000`
- **Backend API**: `http://<SERVER_IP>:8000`
- **API Documentation**: `http://<SERVER_IP>:8000/docs`

## Default Credentials

Check database for users or create admin user:
```sql
-- View existing users
SELECT id, email, nom, prenom, role, actif FROM users;

-- Create admin user (if needed)
INSERT INTO users (email, nom, prenom, password_hash, role, actif) 
VALUES (
    'admin@ayhr.dz',
    'Admin',
    'Système',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5QK7TJk/bQhau',
    'Admin',
    1
);
-- Default password: admin123
```

## Updating the Application

```bash
# Stop services
sudo systemctl stop ayhr-backend ayhr-frontend

# Update code (if using git)
cd /opt/ay-hr
git pull origin main

# Or transfer updated files via SCP
scp updated_file.py root@<SERVER_IP>:/opt/ay-hr/path/to/file.py

# Update Python dependencies (if requirements changed)
cd /opt/ay-hr/backend
source .venv/bin/activate
pip install -r requirements.txt

# Update Node dependencies (if package.json changed)
cd /opt/ay-hr/frontend
npm install
npm run build

# Clear Python cache
find /opt/ay-hr/backend -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
find /opt/ay-hr/backend -name '*.pyc' -delete

# Start services
sudo systemctl start ayhr-backend ayhr-frontend
```

## Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow application ports
sudo ufw allow 3000/tcp  # Frontend
sudo ufw allow 8000/tcp  # Backend

# Enable firewall
sudo ufw enable
```

## Backup and Restore

### Database Backup
```bash
# Create backup
mysqldump -uayhr_user -p'!Yara@2014' ay_hr > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
mysql -uayhr_user -p'!Yara@2014' ay_hr < backup_20251116_153000.sql
```

### Application Backup
```bash
# Backup application files
tar -czf ayhr_backup_$(date +%Y%m%d).tar.gz /opt/ay-hr

# Restore
tar -xzf ayhr_backup_20251116.tar.gz -C /
```

## Production Checklist

- [ ] Database secured with strong password
- [ ] `.env` file has production values
- [ ] DEBUG=False in environment
- [ ] Firewall configured
- [ ] Services enabled for auto-start
- [ ] Regular backups scheduled
- [ ] SSL/TLS certificates configured (if using HTTPS)
- [ ] Monitoring/logging configured
- [ ] IRG file present and up-to-date

## Support

For issues or questions:
- Check logs: `journalctl -u ayhr-backend -n 100`
- Review this guide for common issues
- Verify all prerequisites are met
- Check database connectivity and schema

---

**Last Updated**: November 25, 2025  
**Version**: 1.2.4
