import CreateBotForm from '@/components/CreateBotForm';
import { useState } from 'react';

export default function Meetings() {
  const [bots, setBots] = useState<any[]>([]);

  const handleBotCreated = (botId: string) => {
    setBots((prev) => [...prev, { id: botId, createdAt: new Date() }]);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Meeting Management</h1>
        <p className="text-gray-600">
          Create and manage meeting bots.
        </p>
      </div>

      <CreateBotForm onBotCreated={handleBotCreated} />

      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Active Bots</h2>
        {bots.length > 0 ? (
          <div className="space-y-2">
            {bots.map((bot) => (
              <div key={bot.id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Bot ID: {bot.id}</p>
                    <p className="text-sm text-gray-500">
                      Created: {bot.createdAt.toLocaleString()}
                    </p>
                  </div>
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 italic">No active bots. Create one above to get started.</p>
        )}
      </div>
    </div>
  );
}

