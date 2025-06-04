'use client';

import { useState, useEffect } from 'react';
import api, { PromptVersion } from '../../services/api';

interface PromptHistoryProps {
  projectId: string;
  promptId: string;
  onVersionRestore?: () => void;
}

export default function PromptHistory({ 
  projectId, 
  promptId, 
  onVersionRestore 
}: PromptHistoryProps) {
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [restoring, setRestoring] = useState<number | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<PromptVersion | null>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadVersions();
  }, [projectId, promptId]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadVersions = async () => {
    try {
      setLoading(true);
      const data = await api.prompts.getPromptVersions(projectId, promptId);
      setVersions(data);
    } catch (error) {
      console.error('Error loading prompt versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const handleRestoreVersion = async (versionNumber: number) => {
    if (restoring) return;
    
    if (!confirm(`Are you sure you want to restore to version ${versionNumber}? This will replace the current prompt content.`)) {
      return;
    }

    try {
      setRestoring(versionNumber);
      await api.prompts.restorePromptVersion(projectId, promptId, versionNumber);
      
      if (onVersionRestore) {
        onVersionRestore();
      }
      
      alert('Version restored successfully!');
    } catch (error) {
      console.error('Error restoring version:', error);
      alert('Failed to restore version. Please try again.');
    } finally {
      setRestoring(null);
    }
  };

  const viewVersion = (version: PromptVersion) => {
    setSelectedVersion(version);
    setShowModal(true);
  };

  if (loading) {
    return (
      <div className="bg-white shadow-lg rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Version History</h3>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading versions...</span>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Version History</h3>
          <p className="text-sm text-gray-600 mt-1">
            {versions.length} version{versions.length !== 1 ? 's' : ''} available
          </p>
        </div>

        <div className="max-h-96 overflow-y-auto">
          {versions.length === 0 ? (
            <div className="p-6 text-center text-gray-600">
              No versions available yet. Versions are created when you modify the prompt.
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {versions.map((version) => (
                <div key={version.id} className="p-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                          Version {version.version_number}
                        </span>
                        <span className="text-sm text-gray-600">
                          {formatDate(version.created_at)}
                        </span>
                      </div>
                      
                      <div className="mt-2">
                        <p className="text-sm text-gray-700 line-clamp-2">
                          <span className="font-medium">Prompt:</span> {version.prompt_text.substring(0, 100)}
                          {version.prompt_text.length > 100 && '...'}
                        </p>
                        {version.generated_content && (
                          <p className="text-sm text-gray-600 mt-1 line-clamp-1">
                            <span className="font-medium">Generated:</span> {version.generated_content.substring(0, 80)}
                            {version.generated_content.length > 80 && '...'}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => viewVersion(version)}
                        className="bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-medium py-1 px-3 rounded"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleRestoreVersion(version.version_number)}
                        disabled={restoring === version.version_number}
                        className="bg-blue-500 hover:bg-blue-700 disabled:bg-blue-300 text-white text-xs font-medium py-1 px-3 rounded"
                      >
                        {restoring === version.version_number ? 'Restoring...' : 'Restore'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Version View Modal */}
      {showModal && selectedVersion && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Version {selectedVersion.version_number} Details
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4 max-h-96 overflow-y-auto">
              <div>
                <p className="text-sm text-gray-600 mb-2">
                  Created: {formatDate(selectedVersion.created_at)}
                </p>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-2">Prompt Text:</h4>
                <div className="bg-gray-50 p-4 rounded-md border">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                    {selectedVersion.prompt_text}
                  </pre>
                </div>
              </div>

              {selectedVersion.generated_content && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Generated Content:</h4>
                  <div className="bg-gray-50 p-4 rounded-md border">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                      {selectedVersion.generated_content}
                    </pre>
                  </div>
                </div>
              )}
            </div>

            <div className="flex justify-end space-x-3 mt-6 pt-4 border-t">
              <button
                onClick={() => setShowModal(false)}
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded"
              >
                Close
              </button>
              <button
                onClick={() => {
                  handleRestoreVersion(selectedVersion.version_number);
                  setShowModal(false);
                }}
                disabled={restoring === selectedVersion.version_number}
                className="bg-blue-500 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-2 px-4 rounded"
              >
                {restoring === selectedVersion.version_number ? 'Restoring...' : 'Restore This Version'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}