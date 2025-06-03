'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { sanitizePromptText } from '../../utils/validation';

// Esquema de validación para proyectos
const projectSchema = z.object({
  name: z.string().min(3, { message: 'El nombre debe tener al menos 3 caracteres' }),
  description: z.string().min(10, { message: 'La descripción debe tener al menos 10 caracteres' }).optional(),
  idea_text: z.string().min(20, { message: 'La idea debe tener al menos 20 caracteres' })
    .refine(
      (text) => {
        // Palabras clave que deben estar presentes en un prompt de "Vibe Coding"
        const vibeCodingKeywords = ['vibe', 'coding', 'desarrollo', 'proyecto', 'feature'];
        return vibeCodingKeywords.some(keyword => 
          text.toLowerCase().includes(keyword.toLowerCase())
        );
      },
      { message: 'La idea debe contener al menos una palabra clave de Vibe Coding' }
    ),
  vibe_coding_tags: z.array(z.string()).min(1, { message: 'Debes seleccionar al menos una etiqueta' }).optional(),
  is_public: z.boolean().optional(),
});

type ProjectFormData = z.infer<typeof projectSchema>;

interface ProjectFormProps {
  initialData?: Partial<ProjectFormData>;
  onSubmit: (data: ProjectFormData) => Promise<void>;
  isSubmitting?: boolean;
}

export default function ProjectForm({ initialData, onSubmit, isSubmitting = false }: ProjectFormProps) {
  const [serverError, setServerError] = useState<string | null>(null);
  const [tags, setTags] = useState<string[]>(initialData?.vibe_coding_tags || []);
  const [tagInput, setTagInput] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: initialData?.name || '',
      description: initialData?.description || '',
      idea_text: initialData?.idea_text || '',
      vibe_coding_tags: initialData?.vibe_coding_tags || [],
      is_public: initialData?.is_public || false,
    },
  });

  const addTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      const newTags = [...tags, tagInput.trim()];
      setTags(newTags);
      setValue('vibe_coding_tags', newTags);
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    const newTags = tags.filter(tag => tag !== tagToRemove);
    setTags(newTags);
    setValue('vibe_coding_tags', newTags);
  };

  const handleFormSubmit = async (data: ProjectFormData) => {
    try {
      setServerError(null);
      
      // Sanitizar el texto de la idea antes de enviarlo
      const sanitizedData = {
        ...data,
        idea_text: sanitizePromptText(data.idea_text),
        description: data.description ? sanitizePromptText(data.description) : undefined,
      };
      
      await onSubmit(sanitizedData);
    } catch (error) {
      console.error('Error al enviar el proyecto:', error);
      setServerError('Error al enviar el proyecto. Por favor, inténtalo de nuevo.');
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
          Nombre del Proyecto *
        </label>
        <input
          type="text"
          id="name"
          className={`mt-1 block w-full rounded-md border ${errors.name ? 'border-red-500' : 'border-gray-300'} shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
          {...register('name')}
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Descripción
        </label>
        <textarea
          id="description"
          rows={3}
          className={`mt-1 block w-full rounded-md border ${errors.description ? 'border-red-500' : 'border-gray-300'} shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
          {...register('description')}
        />
        {errors.description && (
          <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="idea_text" className="block text-sm font-medium text-gray-700">
          Idea del Proyecto (estilo Vibe Coding) *
        </label>
        <textarea
          id="idea_text"
          rows={5}
          className={`mt-1 block w-full rounded-md border ${errors.idea_text ? 'border-red-500' : 'border-gray-300'} shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
          placeholder="Describe tu idea en estilo Vibe Coding..."
          {...register('idea_text')}
        />
        {errors.idea_text && (
          <p className="mt-1 text-sm text-red-600">{errors.idea_text.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
          Etiquetas Vibe Coding
        </label>
        <div className="flex items-center">
          <input
            type="text"
            id="tags"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
            className="mt-1 block w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="Añadir etiqueta..."
          />
          <button
            type="button"
            onClick={addTag}
            className="ml-2 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Añadir
          </button>
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          {tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
            >
              {tag}
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="ml-1.5 inline-flex items-center justify-center h-4 w-4 rounded-full text-indigo-400 hover:bg-indigo-200 hover:text-indigo-500 focus:outline-none focus:bg-indigo-500 focus:text-white"
              >
                &times;
              </button>
            </span>
          ))}
        </div>
        {errors.vibe_coding_tags && (
          <p className="mt-1 text-sm text-red-600">{errors.vibe_coding_tags.message}</p>
        )}
      </div>

      <div className="flex items-center">
        <input
          id="is_public"
          type="checkbox"
          className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
          {...register('is_public')}
        />
        <label htmlFor="is_public" className="ml-2 block text-sm text-gray-900">
          Proyecto público
        </label>
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
          {isSubmitting ? 'Guardando...' : 'Guardar Proyecto'}
        </button>
      </div>
    </form>
  );
}