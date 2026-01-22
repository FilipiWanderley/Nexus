const getBaseUrl = () => {
  // Always prioritize environment variable if set
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL
  
  // If running in browser
  if (typeof window !== 'undefined') {
      // Local development
      if (window.location.hostname === 'localhost') {
          return 'http://localhost:8000/api/v1'
      }
      // Production (Vercel) - use absolute URL to avoid fetch issues
      return `${window.location.origin}/api/v1`
  }
  
  // Server-side fallback (should rarely be hit in this app)
  return '/api/v1'
}

const API_URL = getBaseUrl()

export function getSessionId() {
  if (typeof window === 'undefined') return '00000000-0000-0000-0000-000000000000'
  
  let sessionId = localStorage.getItem('nexus_session_id_v2')
  if (!sessionId) {
    // Generate a valid UUID v4
    sessionId = crypto.randomUUID()
    localStorage.setItem('nexus_session_id_v2', sessionId)
  }
  return sessionId
}

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  // No Supabase Auth anymore. We use Session ID for guests.
  const sessionId = getSessionId()
  
  const headers: Record<string, string> = {
    'X-Session-ID': sessionId,
    ...options.headers as Record<string, string>,
  }

  // Remove Content-Type if body is FormData (browser sets it automatically with boundary)
  if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || errorData.error || `Request failed: ${response.status}`)
  }

  return response.json()
}

export async function optimizeResume(
  resumeId: string,
  jobDescription: string,
  missingCritical: string[],
  missingBonus: string[],
  suggestions: string[],
  resumeText?: string
) {
  return fetchWithAuth('/analysis/optimize', {
    method: 'POST',
    body: JSON.stringify({
      resume_id: resumeId,
      resume_text: resumeText,
      job_description: jobDescription,
      missing_critical_skills: missingCritical,
      missing_bonus_skills: missingBonus,
      suggestions: suggestions
    })
  })
}
