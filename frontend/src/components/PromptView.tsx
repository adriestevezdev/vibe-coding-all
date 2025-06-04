'use client';

import { useState, useRef, useEffect } from 'react';
import { Prompt } from '../../types/prompt';
import { saveAs } from 'file-saver';
import jsPDF from 'jspdf';
import api from '../../services/api';

interface PromptViewProps {
  prompt: Prompt;
}

export default function PromptView({ prompt }: PromptViewProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (prompt.status === 'generating' && !prompt.generated_content) {
      setIsGenerating(true);
      const interval = setInterval(async () => {
        try {
          window.location.reload();
        } catch (error) {
          console.error('Error checking generation status:', error);
        }
      }, 3000);

      return () => clearInterval(interval);
    } else {
      setIsGenerating(false);
    }
  }, [prompt.status, prompt.generated_content]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const exportAsJSON = () => {
    const exportData = {
      id: prompt.id,
      prompt_text: prompt.prompt_text,
      generated_content: prompt.generated_content,
      status: prompt.status,
      created_at: prompt.created_at,
      updated_at: prompt.updated_at,
      prompt_type: prompt.prompt_type,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json;charset=utf-8',
    });
    saveAs(blob, `prompt-${prompt.id}.json`);
  };

  const exportAsMarkdown = () => {
    const markdownContent = `# Prompt Details

## Created: ${formatDate(prompt.created_at)}
## Status: ${prompt.status}
${prompt.prompt_type ? `## Type: ${prompt.prompt_type}` : ''}

## Original Prompt

\`\`\`
${prompt.prompt_text}
\`\`\`

## Generated Content

${prompt.generated_content || 'No content generated yet.'}

---
*Exported from Vibe Coding on ${new Date().toLocaleString()}*
`;

    const blob = new Blob([markdownContent], {
      type: 'text/markdown;charset=utf-8',
    });
    saveAs(blob, `prompt-${prompt.id}.md`);
  };

  const exportAsPDF = () => {
    const pdf = new jsPDF();
    const pageWidth = pdf.internal.pageSize.getWidth();
    const margin = 20;
    const maxWidth = pageWidth - 2 * margin;

    pdf.setFontSize(20);
    pdf.text('Prompt Details', margin, 30);

    pdf.setFontSize(12);
    let yPosition = 50;

    pdf.text(`Created: ${formatDate(prompt.created_at)}`, margin, yPosition);
    yPosition += 10;

    pdf.text(`Status: ${prompt.status}`, margin, yPosition);
    yPosition += 10;

    if (prompt.prompt_type) {
      pdf.text(`Type: ${prompt.prompt_type}`, margin, yPosition);
      yPosition += 20;
    } else {
      yPosition += 10;
    }

    pdf.setFontSize(14);
    pdf.text('Original Prompt:', margin, yPosition);
    yPosition += 10;

    pdf.setFontSize(10);
    const promptLines = pdf.splitTextToSize(prompt.prompt_text, maxWidth);
    pdf.text(promptLines, margin, yPosition);
    yPosition += promptLines.length * 5 + 15;

    if (yPosition > 250) {
      pdf.addPage();
      yPosition = 30;
    }

    pdf.setFontSize(14);
    pdf.text('Generated Content:', margin, yPosition);
    yPosition += 10;

    pdf.setFontSize(10);
    const content = prompt.generated_content || 'No content generated yet.';
    const contentLines = pdf.splitTextToSize(content, maxWidth);
    
    contentLines.forEach((line: string) => {
      if (yPosition > 270) {
        pdf.addPage();
        yPosition = 30;
      }
      pdf.text(line, margin, yPosition);
      yPosition += 5;
    });

    pdf.setFontSize(8);
    pdf.text(`Exported from Vibe Coding on ${new Date().toLocaleString()}`, margin, pdf.internal.pageSize.getHeight() - 10);

    pdf.save(`prompt-${prompt.id}.pdf`);
  };

  const sharePrompt = async () => {
    if (isSharing) return;
    
    setIsSharing(true);
    try {
      const result = await api.prompts.createShareLink(prompt.id);
      const fullUrl = `${window.location.origin}${result.share_url}`;
      setShareUrl(fullUrl);
      
      // Copy to clipboard
      await navigator.clipboard.writeText(fullUrl);
      alert('Share link copied to clipboard!');
    } catch (error) {
      console.error('Error creating share link:', error);
      alert('Failed to create share link. Please try again.');
    } finally {
      setIsSharing(false);
    }
  };

  return (
    <div className="bg-white shadow-lg rounded-lg overflow-hidden">
      {/* Header with export buttons */}
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
          
          <div className="flex space-x-2">
            <button
              onClick={sharePrompt}
              disabled={isSharing}
              className="bg-purple-500 hover:bg-purple-700 disabled:bg-purple-300 text-white text-sm font-bold py-2 px-3 rounded"
            >
              {isSharing ? 'Creating...' : 'Share'}
            </button>
            <button
              onClick={exportAsJSON}
              className="bg-blue-500 hover:bg-blue-700 text-white text-sm font-bold py-2 px-3 rounded"
            >
              Export JSON
            </button>
            <button
              onClick={exportAsMarkdown}
              className="bg-green-500 hover:bg-green-700 text-white text-sm font-bold py-2 px-3 rounded"
            >
              Export MD
            </button>
            <button
              onClick={exportAsPDF}
              className="bg-red-500 hover:bg-red-700 text-white text-sm font-bold py-2 px-3 rounded"
            >
              Export PDF
            </button>
          </div>
        </div>
      </div>

      <div ref={contentRef} className="p-6">
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
          
          {isGenerating ? (
            <div className="bg-yellow-50 border border-yellow-200 p-6 rounded-md">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-yellow-600 mr-3"></div>
                <div>
                  <h4 className="font-medium text-yellow-800">Generating Content...</h4>
                  <p className="text-sm text-yellow-700 mt-1">
                    Please wait while AI generates your content. This page will automatically refresh.
                  </p>
                </div>
              </div>
            </div>
          ) : prompt.generated_content ? (
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

        {/* Metadata */}
        <div className="border-t border-gray-200 pt-4">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Metadata</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">ID:</span>
              <span className="ml-2 text-gray-600 font-mono">{prompt.id}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Project ID:</span>
              <span className="ml-2 text-gray-600 font-mono">{prompt.project_id}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Created:</span>
              <span className="ml-2 text-gray-600">{formatDate(prompt.created_at)}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Updated:</span>
              <span className="ml-2 text-gray-600">{formatDate(prompt.updated_at)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}