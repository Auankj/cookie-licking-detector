# 🍪 Cookie-Licking Detector - Web Application

## Overview

A professional, fully-functional web dashboard for the Cookie-Licking Detector system. This single-page application provides a beautiful interface for monitoring repositories, tracking claims, and viewing analytics.

## Features

### 📊 Dashboard
- **Real-time Statistics**: View total repositories, active claims, completed claims, and nudges sent
- **Live Charts**: Visual representation of claims trends and status distribution
- **Recent Activity Feed**: Monitor all system activities in real-time
- **Auto-refresh**: Dashboard updates automatically every 30 seconds

### 📦 Repository Management
- **Browse Repositories**: View all monitored repositories with detailed statistics
- **Add New Repositories**: Easy form to add GitHub repositories for monitoring
- **Search & Filter**: Quickly find repositories by name or status
- **Repository Stats**: See active claims, total issues, grace period, and nudge count

### 🎯 Claims Tracking
- **View All Claims**: Complete list of all issue claims across repositories
- **Filter by Status**: Filter claims by active, completed, released, or expired
- **Search Claims**: Find specific claims by issue title or number
- **Claim Details**: View confidence scores, timestamps, and user information

### 📈 Analytics
- **Performance Metrics**: Average claim duration, completion rate, detection accuracy
- **Contributor Insights**: Track active contributors and top performers
- **Visual Charts**: Response time distribution and top contributors

### 📚 API Documentation
- **Direct Access**: Links to Swagger UI, ReDoc, and OpenAPI specification
- **Authentication Guide**: Quick start guide for API usage
- **Health Monitoring**: Check API health and system status

## Technology Stack

- **Frontend**: Vanilla JavaScript (no frameworks - lightweight and fast)
- **Styling**: Modern CSS with CSS Variables
- **Architecture**: Single-Page Application (SPA)
- **API**: RESTful API with JWT authentication
- **Responsive**: Mobile-friendly design

## Access

### Web Application
```
http://localhost:8000/
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### API Root
```
http://localhost:8000/api
```

## Usage

### 1. Start the Server
```bash
cd /Users/void/Desktop/CookiesCop/cookie-licking-detector
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Open Your Browser
Navigate to: http://localhost:8000/

### 3. Login (Optional)
Click the "Login" button in the navigation bar to authenticate and access protected features.

**Default Test Credentials** (if configured):
- Username: admin
- Password: admin

### 4. Explore Features

#### Dashboard
- View real-time statistics
- Monitor recent activity
- Check system performance

#### Repositories
- Browse all monitored repositories
- Add new repositories with the "+ Add Repository" button
- Search and filter repositories

#### Claims
- View all issue claims
- Filter by status (active, completed, released, expired)
- Search for specific claims

#### Analytics
- View performance metrics
- Analyze contributor statistics
- Explore charts and insights

#### API Docs
- Access interactive API documentation
- Test API endpoints
- Download OpenAPI specification

## Features in Detail

### Authentication
- **JWT-based**: Secure token-based authentication
- **Session Persistence**: Stays logged in across browser sessions
- **Auto-logout**: Automatically logs out on 401 responses

### Real-time Updates
- **Auto-refresh**: Dashboard updates every 30 seconds
- **Live Data**: All statistics and charts reflect current state
- **Activity Feed**: See system events as they happen

### Responsive Design
- **Mobile-friendly**: Works on all device sizes
- **Modern UI**: Clean, professional interface
- **Smooth Animations**: Polished user experience

### User Experience
- **Toast Notifications**: Non-intrusive success/error messages
- **Loading Indicators**: Clear feedback during data fetching
- **Error Handling**: Graceful error messages with helpful information
- **Search & Filter**: Find information quickly

## File Structure

```
static/webapp/
├── index.html          # Main HTML structure
├── styles.css          # Complete CSS styling
└── app.js             # Application logic and API integration
```

## API Integration

The web app integrates with the following API endpoints:

### Dashboard
- `GET /api/v1/dashboard/stats` - System statistics
- `GET /api/v1/dashboard/activity` - Recent activity feed
- `GET /api/v1/dashboard/analytics` - Analytics data

### Repositories
- `GET /api/v1/repositories` - List all repositories
- `POST /api/v1/repositories` - Add new repository

### Claims
- `GET /api/v1/claims` - List all claims
- `GET /api/v1/claims?status=active` - Filter claims by status

### Authentication
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/users/me` - Get current user info

## Customization

### Colors
Edit CSS variables in `styles.css`:
```css
:root {
    --primary-color: #667eea;
    --secondary-color: #48bb78;
    --danger-color: #f56565;
    /* ... */
}
```

### Auto-refresh Interval
Edit in `app.js`:
```javascript
setInterval(() => {
    // ...
}, 30000); // Change 30000 to desired milliseconds
```

### API Base URL
If deploying to a different domain, update in `app.js`:
```javascript
const API_BASE_URL = window.location.origin + '/api/v1';
```

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Security

- **JWT Authentication**: Secure token-based auth
- **HTTPS Ready**: Works with SSL/TLS
- **XSS Protection**: Proper escaping and sanitization
- **CORS Configured**: Secure cross-origin requests

## Performance

- **Lightweight**: No heavy frameworks (< 100KB total)
- **Fast Loading**: Minimal dependencies
- **Optimized**: Efficient API calls and caching
- **Responsive**: Smooth animations and transitions

## Troubleshooting

### Web App Not Loading
1. Check if the server is running on port 8000
2. Verify files exist in `static/webapp/` directory
3. Check browser console for errors

### API Errors
1. Ensure backend server is running
2. Check if you're logged in (for protected endpoints)
3. Verify API base URL is correct

### Login Issues
1. Verify credentials are correct
2. Check if authentication is enabled in backend
3. Clear browser cache and try again

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Chart library integration (Chart.js/D3.js)
- [ ] Export data to CSV/JSON
- [ ] Advanced filtering and sorting
- [ ] Dark mode theme
- [ ] Customizable dashboards
- [ ] Notification system
- [ ] User preferences

## License

Part of the Cookie-Licking Detector project.

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review server logs
3. Open an issue on GitHub

---

**Built with ❤️ for the Cookie-Licking Detector project**
