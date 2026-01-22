'use client'

import { useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { createClient } from '@/utils/supabase/client'
import { Loader2 } from 'lucide-react'

function AuthCallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const supabase = createClient()

  useEffect(() => {
    const handleAuth = async () => {
      try {
        // Check if there's a code to exchange (PKCE flow)
        const code = searchParams.get('code')
        if (code) {
          const { error } = await supabase.auth.exchangeCodeForSession(code)
          if (error) throw error
        }

        // Check for session (Implicit flow or after exchange)
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()
        
        if (sessionError) throw sessionError

        if (session) {
          router.push('/dashboard')
        } else {
          router.push('/login')
        }
      } catch (error) {
        console.error('Auth error:', error)
        router.push('/login?error=AuthFailed')
      }
    }

    handleAuth()
  }, [router, searchParams, supabase.auth])

  return (
    <div className="flex flex-col items-center gap-4 text-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <div className="space-y-2">
        <h1 className="text-xl font-semibold">Completing sign in...</h1>
        <p className="text-sm text-muted-foreground">Please wait while we redirect you.</p>
      </div>
    </div>
  )
}

export default function AuthCallbackPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Suspense fallback={<Loader2 className="h-8 w-8 animate-spin text-primary" />}>
        <AuthCallbackContent />
      </Suspense>
    </div>
  )
}
