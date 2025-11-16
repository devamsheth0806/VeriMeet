# VeriMeet Frontend

React/Next.js frontend for VeriMeet - Real-time meeting assistant dashboard.

## 🚀 Features

- **Real-time Dashboard**: Live updates of meeting transcripts, summaries, facts, and intents
- **Meeting Management**: Create and manage meeting bots
- **Visual Status**: Connection status, API health, and system information
- **Modern UI**: Built with Next.js, React, TypeScript, and Tailwind CSS

## 📋 Prerequisites

- Node.js 18+ and npm/yarn
- Backend server running on `http://localhost:8000`

## 🛠️ Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure environment (optional):**
   Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
   ```

## 🏃 Running

### Development Mode

```bash
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:3000`

### Production Build

```bash
npm run build
npm start
# or
yarn build
yarn start
```

## 📁 Project Structure

```
frontend/
├── components/          # React components
│   ├── Layout.tsx      # Main layout with navigation
│   ├── CreateBotForm.tsx  # Form to create meeting bots
│   └── MeetingDashboard.tsx  # Real-time meeting dashboard
├── lib/                # Utilities and API clients
│   ├── api.ts          # API client for backend
│   └── websocket.ts    # WebSocket hook for real-time updates
├── pages/              # Next.js pages
│   ├── index.tsx       # Dashboard (home page)
│   ├── meetings.tsx    # Meeting management
│   ├── settings.tsx    # Settings and status
│   └── _app.tsx        # App wrapper
├── styles/              # Global styles
└── public/               # Static assets

```

## 🎨 Pages

### Dashboard (`/`)
- Create meeting bots
- Real-time meeting updates
- Live transcripts
- Verified facts
- Detected intents
- Meeting summaries

### Meetings (`/meetings`)
- Create new meeting bots
- View active bots
- Manage bot sessions

### Settings (`/settings`)
- API health status
- Configuration information
- Feature overview

## 🔌 API Integration

The frontend connects to the FastAPI backend:

- **REST API**: `http://localhost:8000`
  - `GET /` - Health check
  - `POST /api/create-bot` - Create meeting bot
  - `GET /api/summary` - Get current summary

- **WebSocket**: `ws://localhost:8000/ws`
  - Real-time event streaming
  - Transcript updates
  - Fact verification results
  - Intent detection
  - Summary updates

## 🎯 Usage

1. **Start the backend server:**
   ```bash
   cd ..
   python3 server.py
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

4. **Create a bot:**
   - Go to Dashboard or Meetings page
   - Enter a Google Meet URL
   - Click "Create Bot"
   - Watch real-time updates!

## 🛠️ Development

### Adding New Components

Components are in the `components/` directory. Use TypeScript for type safety.

### Styling

Uses Tailwind CSS. Customize colors in `tailwind.config.js`.

### API Client

The API client is in `lib/api.ts`. Add new endpoints as needed.

### WebSocket

The WebSocket hook is in `lib/websocket.ts`. It automatically reconnects on disconnect.

## 🐛 Troubleshooting

### Frontend won't connect to backend
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS is enabled in backend

### WebSocket not connecting
- Check backend WebSocket endpoint is active
- Verify `NEXT_PUBLIC_WS_URL` in `.env.local`
- Check browser console for errors

### Build errors
- Clear `.next` directory: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`

## 📚 Technologies

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **WebSocket API** - Real-time communication
- **Lucide React** - Icons
- **date-fns** - Date formatting

## 📝 License

Same as main VeriMeet project.

