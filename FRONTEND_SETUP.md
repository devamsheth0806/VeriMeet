# 🎨 VeriMeet Frontend Setup Guide

Complete guide to set up and run the React/Next.js frontend.

## ✅ What's Included

- **Real-time Dashboard** - Live meeting updates
- **Meeting Management** - Create and manage bots
- **Settings Page** - API status and configuration
- **Modern UI** - Built with Next.js, TypeScript, and Tailwind CSS

## 📋 Prerequisites

1. **Node.js 18+** installed
   ```bash
   node --version  # Should be 18 or higher
   ```

2. **Backend server running** on `http://localhost:8000`
   - Make sure you've started the Python backend first!

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

### Step 2: Start Development Server

```bash
npm run dev
```

The frontend will be available at **http://localhost:3000**

### Step 3: Open in Browser

Navigate to `http://localhost:3000` and you should see the VeriMeet dashboard!

## 📁 Project Structure

```
frontend/
├── components/          # React components
│   ├── Layout.tsx       # Navigation and layout
│   ├── CreateBotForm.tsx    # Bot creation form
│   └── MeetingDashboard.tsx # Real-time dashboard
├── lib/                 # Utilities
│   ├── api.ts           # API client
│   └── websocket.ts     # WebSocket hook
├── pages/               # Next.js pages
│   ├── index.tsx        # Dashboard (home)
│   ├── meetings.tsx      # Meeting management
│   └── settings.tsx     # Settings page
└── styles/              # Global styles
```

## 🎯 Features

### Dashboard (`/`)
- Create meeting bots
- Real-time transcript updates
- Live fact verification
- Intent detection display
- Meeting summaries

### Meetings (`/meetings`)
- Create new bots
- View active bots
- Manage sessions

### Settings (`/settings`)
- API health check
- Connection status
- Configuration info

## 🔧 Configuration

### Environment Variables (Optional)

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

**Note:** These are optional - defaults work for local development.

## 🏃 Running Both Backend and Frontend

### Terminal 1: Backend
```bash
# In project root
python3 server.py
```

### Terminal 2: Frontend
```bash
# In frontend directory
cd frontend
npm run dev
```

### Browser
Open `http://localhost:3000`

## 🧪 Testing

1. **Start backend:**
   ```bash
   python3 server.py
   ```

2. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test the dashboard:**
   - Go to `http://localhost:3000`
   - Try creating a bot with a Google Meet URL
   - Watch real-time updates!

## 🐛 Troubleshooting

### "Cannot connect to API"
- ✅ Make sure backend is running on port 8000
- ✅ Check `python3 server.py` is running
- ✅ Verify CORS is enabled in backend (it is!)

### "WebSocket connection failed"
- ✅ Backend must be running
- ✅ Check WebSocket endpoint: `ws://localhost:8000/ws`
- ✅ Look for errors in browser console

### "Module not found" errors
```bash
cd frontend
rm -rf node_modules
npm install
```

### Build errors
```bash
cd frontend
rm -rf .next
npm run build
```

## 📦 Production Build

```bash
cd frontend
npm run build
npm start
```

This creates an optimized production build.

## 🎨 Customization

### Colors
Edit `tailwind.config.js` to change the color scheme.

### API URL
Change `NEXT_PUBLIC_API_URL` in `.env.local` or `next.config.js`.

### Components
All components are in `components/` - modify as needed!

## 📚 Technologies Used

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **WebSocket API** - Real-time updates
- **Lucide React** - Icons

## ✅ Next Steps

1. ✅ Install dependencies: `npm install`
2. ✅ Start backend: `python3 server.py`
3. ✅ Start frontend: `npm run dev`
4. ✅ Open browser: `http://localhost:3000`
5. ✅ Create a bot and watch it work!

---

**Enjoy your new VeriMeet dashboard! 🎉**

