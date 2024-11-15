
# Deployment Steps

## Prepare the Linux Server
1. Install necessary dependencies:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx
   ```

## Clone the Repository
1. Clone application’s repository to the server:

## Set Up the Python Environment
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Test the Application Locally
1. Run the Flask app to ensure it works:
   ```bash
   python app.py
   ```

## Configure Gunicorn
1. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```
2. Test Gunicorn:
   ```bash
   gunicorn --bind 0.0.0.0:5000 app:app
   ```

## Set Up Nginx
1. Configure Nginx as a reverse proxy:
   - Create an Nginx configuration file:
     ```bash
     sudo nano /etc/nginx/sites-available/flask_app
     ```
   - Content for the file:
     ```nginx
     server {
         listen 80;
         server_name your-domain.com;

         location / {
             proxy_pass http://127.0.0.1:5000;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
         }
     }
     ```
2. Enable the configuration:
   ```bash
   sudo ln -s /etc/nginx/sites-available/flask_app /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Run Flask App as a Service
1. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/flask_app.service
   ```
2. Content for the file:
   ```ini
   [Unit]
   Description=Gunicorn instance to serve Flask app
   After=network.target

   [Service]
   User=your-username
   Group=www-data
   WorkingDirectory=/path/to/your/app
   ExecStart=/path/to/your/app/venv/bin/gunicorn --workers 3 --bind unix:flask_app.sock -m 007 wsgi:app

   [Install]
   WantedBy=multi-user.target
   ```
3. Enable and start the service:
   ```bash
   sudo systemctl start flask_app
   sudo systemctl enable flask_app
   ```

## Secure the Server
1. Use `ufw` to allow only necessary ports:
   ```bash
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   ```
2. Install SSL (e.g., with Certbot for Let’s Encrypt):
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx
   ```

## Test and Monitor
1. Ensure the app is accessible via the domain.
2. Monitor logs for issues:
   ```bash
   sudo journalctl -u flask_app
   sudo tail -f /var/log/nginx/access.log
   ```
