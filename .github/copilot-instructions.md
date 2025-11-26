# Django Real-Time Chat Platform

This is a Django-based customer support chat platform with the following features:

## Architecture
- **Backend**: Django + Django REST Framework
- **Real-time**: Django Channels + Redis  
- **Database**: PostgreSQL for persistent messages
- **Frontend**: Embeddable JavaScript widget + Admin dashboard

## Components
- Customer chat widget (embeddable)
- Admin dashboard for conversation management
- Real-time WebSocket communication
- Persistent message storage
- File attachment support

## Development Guidelines
- Use Django apps: `chat`, `accounts`, `dashboard`
- Implement proper WebSocket consumers for real-time messaging
- Create RESTful API endpoints for chat operations
- Ensure responsive design for admin dashboard
- Follow Django best practices for security and performance