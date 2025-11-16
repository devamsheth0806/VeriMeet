import { useState } from 'react';
import { apiClient, BotCreationRequest } from '@/lib/api';
import { Send, Loader2 } from 'lucide-react';

interface CreateBotFormProps {
  onBotCreated?: (botId: string) => void;
}

export default function CreateBotForm({ onBotCreated }: CreateBotFormProps) {
  const [meetingUrl, setMeetingUrl] = useState('');
  const [botName, setBotName] = useState('VeriMeet Assistant');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const data: BotCreationRequest = {
        meeting_url: meetingUrl,
        bot_name: botName || 'VeriMeet Assistant',
      };

      const response = await apiClient.createBot(data);

      if (response.success && response.bot_id) {
        setSuccess(`Bot created successfully! Bot ID: ${response.bot_id}`);
        setMeetingUrl('');
        if (onBotCreated) {
          onBotCreated(response.bot_id);
        }
      } else {
        setError(response.error || 'Failed to create bot');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Create Meeting Bot</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="meetingUrl" className="block text-sm font-medium text-gray-700 mb-1">
            Meeting URL
          </label>
          <input
            type="url"
            id="meetingUrl"
            value={meetingUrl}
            onChange={(e) => setMeetingUrl(e.target.value)}
            placeholder="https://meet.google.com/xxx-xxxx-xxx"
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        <div>
          <label htmlFor="botName" className="block text-sm font-medium text-gray-700 mb-1">
            Bot Name (optional)
          </label>
          <input
            type="text"
            id="botName"
            value={botName}
            onChange={(e) => setBotName(e.target.value)}
            placeholder="VeriMeet Assistant"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {success}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
              Creating Bot...
            </>
          ) : (
            <>
              <Send className="w-4 h-4 mr-2" />
              Create Bot
            </>
          )}
        </button>
      </form>
    </div>
  );
}

