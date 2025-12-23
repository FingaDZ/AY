-- Fix logging table action_type ENUM to support LOGIN
ALTER TABLE logging 
MODIFY action_type ENUM('CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'VIEW', 'EXPORT', 'IMPORT') NOT NULL;
