'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { promptSchema, sanitizePromptText } from '../../utils/validation';
import { PromptCreate } from '../../types/prompt';

interface PromptFormProps {
  projectId: string;
  onSubmit: (data: PromptCreate) => Promise<void>;
  isSubmitting?: boolean;
}

export default function PromptForm({ projectId, onSubmit, isSubmitting = false }: PromptFormProps) {
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<PromptCreate>({
    resolver: zodResolver(promptSchema),
    defaultValues: {
      project_id: projectId,
      prompt_text: '',
      prompt_type: 'feature',
    },
  });

  const handleFormSubmit = async (data: PromptCreate) => {
    try {
      setServerError(null);
      
      // Sanitizar el texto del prompt antes de enviarlo
      const sanitizedData = {
        ...data,
        prompt_text: sanitizePromptText(data.prompt_text),
      };
      
      await onSubmit(sanitizedData);
      reset(); // Limpiar el formulario después de enviar con éxito
    } catch (error) {
      console.error('Error al enviar el prompt:', error);
      setServerError('Error al enviar el prompt. Por favor, inténtalo de nuevo.');
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      <div>
        <label htmlFor="prompt_text" className="block text-sm font-medium text-gray-700">
          Prompt
        </label>
        <textarea
          id="prompt_text"
          rows={4}
          className={`mt-1 block w-full rounded-md border ${errors.prompt_text ? 'border-red-500' : 'border-gray-300'} shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
          placeholder="Describe tu feature en estilo Vibe Coding..."
          {...register('prompt_text')}
        />
        {errors.prompt_text && (
          <p className="mt-1 text-sm text-red-600">{errors.prompt_text.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="prompt_type" className="block text-sm font-medium text-gray-700">
          Tipo de Prompt
        </label>
        <select
          id="prompt_type"
          className="mt-1 block w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          {...register('prompt_type')}
        >
          <option value="feature">Feature</option>
          <option value="bug">Bug</option>
          <option value="improvement">Mejora</option>
          <option value="documentation">Documentación</option>
        </select>
        {errors.prompt_type && (
          <p className="mt-1 text-sm text-red-600">{errors.prompt_type.message}</p>
        )}
      </div>

      {serverError && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{serverError}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {isSubmitting ? 'Enviando...' : 'Enviar Prompt'}
        </button>
      </div>
    </form>
  );
}