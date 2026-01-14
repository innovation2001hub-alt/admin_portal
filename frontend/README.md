# Admin Portal Frontend

React frontend for the Django Admin Portal with authentication.

## Features

✅ Login page with modern UI
✅ Protected routes
✅ Token-based authentication
✅ Dashboard with user info
✅ Logout functionality

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server 

Make sure your Django backend is running on `http://127.0.0.1:8000`

```bash
npm run dev
```

The frontend will run on: **http://localhost:3000**

### 3. Login

Use one of these credentials:

- **Username:** `admin`
- **Password:** (the one you set for admin)

Or

- **Username:** `manager1`
- **Password:** `manager123`

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Login.jsx           # Login page
│   │   ├── Login.css
│   │   ├── Dashboard.jsx       # Dashboard (after login)
│   │   ├── Dashboard.css
│   │   └── ProtectedRoute.jsx  # Route protection
│   ├── context/
│   │   └── AuthContext.jsx     # Auth state management
│   ├── services/
│   │   └── api.js              # API calls to Django
│   ├── App.jsx                 # Main app with routing
│   ├── App.css
│   └── main.jsx                # Entry point
├── index.html
├── package.json
└── vite.config.js
```

## API Integration

The frontend connects to these Django endpoints:

- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/current-user/` - Get user info

## Building for Production

```bash
npm run build
```

Builds to `dist/` folder.

## Next Steps

Add more features:
- User management pages
- Unit hierarchy viewer
- Approval workflow UI
- Audit log viewer
- Role management

## Technologies

- React 18
- React Router v6
- Axios
- Vite (build tool)
