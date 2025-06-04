'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import api from '../../../../../../services/api';
import { Prompt } from '../../../../../../types/prompt';
import PromptView from '../../../../../components/PromptView';
import PromptHistory from '../../../../../components/PromptHistory';

export default function PromptDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [prompt, setPrompt] = useState<Prompt | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const projectId = params.projectId as string;
  const promptId = params.promptId as string;

  const fetchPrompt = async () => {
    try {
      setLoading(true);
      const promptData = await api.prompts.getPrompt(projectId, promptId);
      setPrompt(promptData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load prompt');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId && promptId) {
      fetchPrompt();
    }
  }, [projectId, promptId]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleVersionRestore = () => {
    // Refresh the prompt data after version restore
    fetchPrompt();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.back()}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!prompt) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-600 mb-4">Prompt Not Found</h2>
          <button
            onClick={() => router.back()}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <button
          onClick={() => router.back()}
          className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded mb-4"
        >
          ← Back
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Prompt Details</h1>
      </div>
      
      <div className="space-y-6">
        <PromptView prompt={prompt} />
        <PromptHistory 
          projectId={projectId} 
          promptId={promptId} 
          onVersionRestore={handleVersionRestore}
        />
      </div>
    </div>
  );
}