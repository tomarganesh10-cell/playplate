-- Create n8n database (shares same postgres instance)
CREATE DATABASE n8n_db;
GRANT ALL PRIVILEGES ON DATABASE n8n_db TO smm;
