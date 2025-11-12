# Telegram Message Link Generator

A production-ready Flask web application that generates unique Telegram message links for secure communication. Perfect for contact forms, feedback collection, and secure messaging.

## 🚀 Features

- **Unique Link Generation**: Create one-time use links for Telegram message delivery
- **Secure Message Sending**: Two-message form with Telegram bot integration
- **Auto-expiration**: Links expire after 24 hours or first use
- **Admin Dashboard**: Protected admin panel to view all generated links and messages
- **API Endpoint**: Generate links programmatically via GET request
- **24/7 Operation**: Keep-alive service for continuous availability
- **Production Ready**: Fully compatible with Render.com free deployment

## 📁 Project Structure

```
telegram_link_generator/
├── web.py              # Main Flask application (production entry point)
├── mainfile.py         # Core Flask functionality
├── keep_alive.py       # 24/7 background service
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── link_generated.html
│   ├── send_message.html
│   ├── message_sent.html
│   ├── link_expired.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── 404.html
│   └── 500.html
└── README.md
```

## ⚡ Quick Start

### 1. Installation

```bash
# Clone or create the project directory
mkdir telegram_link_generator
cd telegram_link_generator

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Locally

```bash
# Start the application
python web.py
```

The application will be available at `http://localhost:5000`

### 3. Deployment on Render.com (Free)

1. **Create new Web Service** on Render.com
2. **Connect your repository** or upload files
3. **Set environment variables**:
   - `PORT=5000`
   - `SECRET_KEY=your-secret-key-here`
   - `RENDER=true`
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `python web.py`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Application port | `5000` |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `RENDER_URL` | Your Render app URL | Auto-detected |
| `DEBUG` | Enable debug mode | `False` |

### Bot Setup

1. **Create Telegram Bot**:
   - Message @BotFather on Telegram
   - Send `/newbot` command
   - Follow instructions to create your bot
   - Save the bot token (format: `1234567890:ABC...`)

2. **Get Admin ID**:
   - Message @userinfobot on Telegram
   - Copy your numeric user ID

3. **Test Bot**:
   - The application will validate your bot token before creating links
   - Invalid tokens will be rejected

## 📊 Usage

### 1. Generate Link (Web Interface)

1. Go to the home page
2. Enter your Telegram Bot Token
3. Enter your Telegram Admin ID
4. Click "Generate Link"
5. Share the unique link

### 2. Generate Link (API)

```bash
GET /api/link?admin_id=123456789&token=1234567890:ABCdef
```

Response:
```json
{
  "success": true,
  "link_id": "ABC12345",
  "link_url": "/send/ABC12345",
  "expires_at": "2024-12-01T10:00:00",
  "bot_username": "your_bot"
}
```

### 3. Send Messages

1. Open the generated link
2. Fill in Message 1 and/or Message 2
3. Click "Send Messages"
4. Messages are delivered to your Telegram

### 4. Admin Dashboard

- **URL**: `/admin`
- **Username**: `mk`
- **Password**: `mk123`

**Change default credentials in production!**

## 🔒 Security Features

- **One-time Use Links**: Each link can only be used once
- **Auto-expiration**: Links expire after 24 hours
- **Input Validation**: All inputs are validated and sanitized
- **Session Management**: Secure session handling
- **Error Handling**: Comprehensive error handling and logging
- **HTTPS Ready**: Compatible with SSL certificates

## 📈 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home page with link generation form |
| `POST` | `/generate_link` | Generate new message link |
| `GET` | `/send/<link_id>` | Message sending page |
| `GET` | `/api/link` | API endpoint for link generation |
| `GET` | `/admin` | Admin login page |
| `POST` | `/admin/login` | Admin login submission |
| `GET` | `/admin/dashboard` | Admin dashboard |
| `GET` | `/admin/logout` | Admin logout |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/cleanup` | Clean up expired links |

## 🛠️ Keep-Alive Service

The `keep_alive.py` script ensures 24/7 operation:

```bash
# Run keep-alive service
python keep_alive.py
```

**Features**:
- Automatic health checks every 5 minutes
- Link cleanup every 30 minutes
- Background threading for continuous operation
- Production and development mode support

## 🎯 Key Components

### 1. Web Application (`web.py`)
- Main Flask application
- Production-ready WSGI configuration
- Error handling and logging
- Security features

### 2. Core Logic (`mainfile.py`)
- Bot token validation
- Link generation and management
- Message delivery system
- Admin functionality

### 3. Templates
- Responsive Bootstrap-based design
- Interactive JavaScript features
- Mobile-friendly interface
- Error pages with helpful information

### 4. Keep-Alive Service
- Health monitoring
- Automatic cleanup
- Background operation
- Logging and monitoring

## 🔧 Customization

### Change Admin Credentials

Edit in `web.py`:
```python
if username == 'your_username' and password == 'your_password':
```

### Modify Link Expiration

Edit expiration time in `web.py`:
```python
expiration_time = datetime.now() + timedelta(hours=24)  # Change hours
```

### Add Database Support

Replace in-memory storage with database:

```python
# Example with SQLite
import sqlite3

def init_db():
    conn = sqlite3.connect('telegram_links.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS links (
        id TEXT PRIMARY KEY,
        bot_token TEXT,
        admin_id TEXT,
        created_at TIMESTAMP,
        used BOOLEAN
    )''')
    conn.commit()
    conn.close()
```

## 📝 Production Deployment

### Render.com (Recommended - Free)

1. **Create account** at [render.com](https://render.com)
2. **New Web Service** → Connect repository
3. **Environment**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python web.py`
4. **Variables**:
   - `PORT=5000`
   - `SECRET_KEY=your-secret-key`
5. **Deploy** and get your URL

### Other Platforms

The application works on any Python hosting platform:

- **Heroku**: Add `Procfile` with `web: python web.py`
- **Railway**: Works out of the box
- **PythonAnywhere**: Upload files and run
- **AWS/GCP/Azure**: Deploy as regular web app

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid bot token"**
   - Check bot token format: `1234567890:ABC...`
   - Ensure bot is created with @BotFather
   - Verify bot is not deleted

2. **"Failed to send messages"**
   - Check admin ID is numeric
   - Ensure bot has permission to message admin
   - Verify bot is not blocked by admin

3. **Application not staying online**
   - Enable keep-alive service
   - Check free tier sleep settings
   - Ensure health endpoints are accessible

4. **Admin panel not loading**
   - Check credentials: username=`mk`, password=`mk123`
   - Clear browser cache
   - Check for JavaScript errors

### Logs

Check application logs for detailed error information:
- Render.com: Dashboard → Logs
- Local: Console output
- Keep-alive: `keep_alive.log`

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support:
1. Check this README
2. Review error logs
3. Test with valid bot tokens
4. Verify admin ID format

---

**Built with ❤️ using Flask and Telegram Bot API**