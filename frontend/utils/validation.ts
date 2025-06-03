import { z } from 'zod';

/**
 * Esquema de validación para prompts estilo "Vibe Coding"
 * 
 * Reglas de validación:
 * - Texto mínimo de 10 caracteres
 * - Debe contener al menos una palabra clave de "Vibe Coding"
 * - No debe contener caracteres especiales no permitidos
 */
export const promptSchema = z.object({
  prompt_text: z
    .string()
    .min(10, { message: 'El prompt debe tener al menos 10 caracteres' })
    .refine(
      (text) => {
        // Palabras clave que deben estar presentes en un prompt de "Vibe Coding"
        const vibeCodingKeywords = ['vibe', 'coding', 'desarrollo', 'proyecto', 'feature'];
        return vibeCodingKeywords.some(keyword => 
          text.toLowerCase().includes(keyword.toLowerCase())
        );
      },
      { message: 'El prompt debe contener al menos una palabra clave de Vibe Coding' }
    ),
  prompt_type: z.string().optional(),
  project_id: z.string().uuid({ message: 'ID de proyecto inválido' }),
});

/**
 * Esquema de validación para actualización de prompts
 */
export const promptUpdateSchema = z.object({
  prompt_text: z
    .string()
    .min(10, { message: 'El prompt debe tener al menos 10 caracteres' })
    .refine(
      (text) => {
        const vibeCodingKeywords = ['vibe', 'coding', 'desarrollo', 'proyecto', 'feature'];
        return vibeCodingKeywords.some(keyword => 
          text.toLowerCase().includes(keyword.toLowerCase())
        );
      },
      { message: 'El prompt debe contener al menos una palabra clave de Vibe Coding' }
    )
    .optional(),
  prompt_type: z.string().optional(),
  status: z.enum(['pending', 'processing', 'completed', 'failed']).optional(),
});

/**
 * Función para sanitizar el texto del prompt
 * Elimina espacios extra y caracteres no deseados
 */
export const sanitizePromptText = (text: string): string => {
  // Eliminar espacios múltiples
  let sanitized = text.replace(/\s+/g, ' ').trim();
  
  // Eliminar caracteres especiales no deseados
  sanitized = sanitized.replace(/[<>{}\[\]\\^~]/g, '');
  
  return sanitized;
};