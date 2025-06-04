'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Prompt } from '../../../../types/prompt';
import api from '../../../../services/api';

export default function SharedPromptPage() {
  const params = useParams();
  const token = params.token as string;
  const [prompt, setPrompt] = useState<Prompt | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSharedPrompt = async () => {
      try {
        setLoading(true);
        setError(null);
        const sharedPrompt = await api.prompts.getSharedPrompt(token);
        setPrompt(sharedPrompt);
      } catch (err) {
        console.error('Error fetching shared prompt:', err);
        setError('This shared link is invalid or has expired.');
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchSharedPrompt();
    }
  }, [token]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md">
          <div className="flex items-center space-x-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="text-lg text-gray-700">Loading shared prompt...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md text-center max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Link Not Found</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <a
            href="/"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Go to Vibe Coding
          </a>
        </div>
      </div>
    );
  }

  if (!prompt) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Shared Prompt</h1>
              <p className="text-sm text-gray-600">View-only access via shared link</p>
            </div>
            <a
              href="/"
              className="bg-blue-500 hover:bg-blue-700 text-white text-sm font-bold py-2 px-4 rounded"
            >
              Create Your Own
            </a>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          {/* Prompt Info */}
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Prompt Content</h2>
                <p className="text-sm text-gray-600 mt-1">
                  Created: {formatDate(prompt.created_at)} | Status: 
                  <span className={`ml-1 px-2 py-1 rounded text-xs font-medium ${
                    prompt.status === 'completed' ? 'bg-green-100 text-green-800' :
                    prompt.status === 'generating' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {prompt.status}
                  </span>
                </p>
              </div>
              <div className="text-sm text-gray-500">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                  Shared Document
                </span>
              </div>
            </div>
          </div>

          <div className="p-6">
            {/* Original Prompt */}
            <div className="mb-8">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Original Prompt</h3>
              <div className="bg-gray-50 p-4 rounded-md border">
                <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                  {prompt.prompt_text}
                </pre>
              </div>
              {prompt.prompt_type && (
                <p className="text-sm text-gray-600 mt-2">Type: {prompt.prompt_type}</p>
              )}
            </div>

            {/* Generated Content */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Generated Content</h3>
              
              {prompt.generated_content ? (
                <div className="bg-white border border-gray-200 rounded-md">
                  <div className="p-4 max-h-96 overflow-y-auto">
                    <div className="prose max-w-none">
                      <pre className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed">
                        {prompt.generated_content}
                      </pre>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-gray-50 border border-gray-200 p-6 rounded-md text-center">
                  <p className="text-gray-600">No content has been generated yet.</p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="border-t border-gray-200 pt-4">
              <div className="text-center">
                <p className="text-sm text-gray-500 mb-4">
                  This document was shared from Vibe Coding
                </p>
                <a
                  href="/"
                  className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded"
                >
                  Try Vibe Coding for Free
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}