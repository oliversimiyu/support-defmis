# DEFMIS Chat Platform

A Django-based real-time customer support chat platform with an embeddable widget and admin dashboard.

## 🚀 Features

- **Real-time Messaging**: WebSocket-based instant messaging with fallback to HTTP API
- **Persistent Conversations**: Messages are saved to database for conversation continuity
- **Embeddable Widget**: JavaScript widget that can be embedded on any website
- **Admin Dashboard**: Comprehensive interface for managing conversations
- **Automated Responses**: Intelligent auto-replies based on keywords, greetings, business hours, and more
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Customizable**: Configure widget appearance, colors, and messages
- **File Attachments**: Support for sending files and images (configurable)
- **Offline Support**: Customers can send messages when offline

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Customer      │    │   Django App    │    │   Admin         │
│   Widget        │◄──►│   + Channels    │◄──►│   Dashboard     │
│   (JavaScript)  │    │   + Redis       │    │   (Web UI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   Database      │
                       └─────────────────┘
```

## 📋 Requirements

- Python 3.8+
- Django 4.2+
- Redis (for WebSocket support)
- PostgreSQL (optional, SQLite included for development)

## 🛠️ Installation & Setup

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd support-defmis

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/chatplatform
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Create default automated responses (optional but recommended)
python manage.py create_default_responses
```

### 4. Start Services

For development:

```bash
# Start Django server with WebSocket support
python manage.py runserver

# In another terminal, start Redis (if not running as service)
redis-server
```

## 🎯 Usage

### Demo Page

Visit `http://localhost:8000/` to see the demo page with the chat widget in action.

### Admin Access

1. **Django Admin**: `http://localhost:8000/admin/`
2. **Chat Dashboard**: `http://localhost:8000/dashboard/`

Default admin credentials (change after first login):
- Username: `admin`
- Password: `admin123`

### Widget Integration

Add the following code to your website before the closing `</body>` tag:

```html
<script>
  window.DEFMISChat = {
    apiUrl: 'http://your-domain.com',
    customerId: null, // Auto-generated if not provided
    customerName: '', // Optional customer name
    customerEmail: '' // Optional customer email
  };
</script>
<script src="http://your-domain.com/static/js/chat-widget.js"></script>
```

## 📱 Admin Dashboard Features

### Dashboard Home
- **Statistics Overview**: Total conversations, open chats, unread messages
- **Recent Activity**: Latest conversations and metrics
- **Real-time Updates**: Auto-refresh for live data

### Conversations Management
- **List View**: All conversations with filtering and search
- **Detail View**: Full conversation history with real-time messaging
- **Status Management**: Open/close conversations
- **Message History**: Persistent conversation threads

### Widget Settings
- **Customization**: Colors, position, welcome messages
- **Integration Code**: Copy-paste code for easy website integration
- **Preview**: Visual preview of widget appearance

### Automated Responses
- **Intelligent Auto-replies**: Trigger responses based on keywords, greetings, and context
- **Business Hours**: Automatically inform customers when outside business hours
- **Offline Detection**: Notify when all agents are busy
- **Customizable Rules**: Create and manage response rules via admin panel
- **Response Logs**: Track which automated responses were sent and when

📚 **Detailed Documentation**: See [AUTOMATED_RESPONSES.md](AUTOMATED_RESPONSES.md) for full automated responses guide.

## 🔧 API Endpoints

### Public API (for widget)
- `GET /chat/api/widget/config/` - Get widget configuration
- `POST /chat/api/chat/start/` - Initialize chat session
- `GET /chat/api/chat/{customer_id}/history/` - Get chat history
- `POST /chat/api/chat/message/` - Send message (HTTP fallback)

### Admin API (authenticated)
- `GET /chat/api/admin/sessions/` - List all chat sessions
- `GET /chat/api/admin/session/{id}/` - Get session details
- `PATCH /chat/api/admin/session/{id}/status/` - Update session status

### WebSocket Endpoints
- `ws://localhost:8000/ws/chat/{customer_id}/` - Customer chat socket
- `ws://localhost:8000/ws/admin/dashboard/` - Admin dashboard socket

## 🏢 Production Deployment

### 1. Environment Setup

```bash
# Set production environment variables
export DEBUG=False
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=postgresql://user:pass@host:5432/dbname
export REDIS_URL=redis://host:6379/0
export ALLOWED_HOSTS=yourdomain.com
```

### 2. Static Files

```bash
python manage.py collectstatic --noinput
```

### 3. ASGI Server

Use Daphne or Uvicorn for production WebSocket support:

```bash
# Option 1: Daphne
daphne -b 0.0.0.0 -p 8000 chatplatform.asgi:application

# Option 2: Uvicorn
uvicorn chatplatform.asgi:application --host 0.0.0.0 --port 8000
```

### 4. Nginx Configuration

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://django;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
}
```

## 🧪 Testing

### Run Tests

```bash
python manage.py test
```

### Manual Testing Checklist

- [ ] Widget loads on demo page
- [ ] Customer can send messages
- [ ] Admin receives messages in real-time
- [ ] Admin can reply to customers
- [ ] Conversation persists after page refresh
- [ ] WebSocket connection works
- [ ] HTTP fallback works when WebSocket fails
- [ ] Mobile responsiveness
- [ ] Multiple concurrent conversations

## 🔍 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check Redis server is running
   - Verify REDIS_URL in settings
   - Check firewall settings for WebSocket ports

2. **Widget Not Loading**
   - Check CORS settings in Django settings
   - Verify static files are served correctly
   - Check browser console for JavaScript errors

3. **Messages Not Persisting**
   - Check database connection
   - Run migrations: `python manage.py migrate`
   - Verify model relationships

4. **Admin Dashboard Not Accessible**
   - Create superuser: `python manage.py createsuperuser`
   - Check LOGIN_URL setting
   - Verify user permissions

### Debug Mode

Enable debug logging in settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'channels': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting guide above
- Review the Django and Channels documentation

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] File attachment handling
- [ ] Typing indicators
- [ ] Message read receipts
- [ ] Automated responses/chatbots
- [ ] Integration with ticketing systems
- [ ] Advanced analytics and reporting
- [ ] Mobile app for admins
- [ ] Video/voice call support