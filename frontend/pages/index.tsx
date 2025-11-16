import { useState } from 'react';
import CreateBotForm from '@/components/CreateBotForm';
import MeetingDashboard from '@/components/MeetingDashboard';

export default function Home() {
  const [activeBotId, setActiveBotId] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">VeriMeet Dashboard</h1>
        <p className="text-gray-600">
          Real-time meeting assistant with fact-checking, summarization, and automation.
        </p>
      </div>

      <CreateBotForm onBotCreated={(botId) => setActiveBotId(botId)} />

      {activeBotId && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Active Bot:</strong> {activeBotId}
          </p>
        </div>
      )}

      <MeetingDashboard />
    </div>
  );
}

