'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/utils/supabase/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from 'sonner'
import { Loader2, AlertCircle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

interface AuthFormProps {
  type: 'login' | 'signup'
}

export function AuthForm({ type }: AuthFormProps) {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const supabase = createClient()

  useEffect(() => {
    // Debug: Check if env vars are loaded
    console.log('Supabase URL configured:', !!process.env.NEXT_PUBLIC_SUPABASE_URL)
  }, [])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      if (type === 'signup') {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: `${window.location.origin}/auth/callback`,
          },
        })
        if (error) throw error
        
        // Success state
        toast.success('Conta criada com sucesso!')
        setError(null) // Clear any previous errors
        
        // Show a more persistent success message in the UI
        alert('Conta criada! Por favor, verifique seu email (e a caixa de Spam) para confirmar o cadastro antes de fazer login.')
        
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        })
        if (error) throw error
        
        toast.success('Login realizado com sucesso!')
        router.refresh()
        router.push('/dashboard')
      }
    } catch (error: any) {
      console.error('Auth error:', error)
      // Translate common errors
      let msg = error.message
      if (msg.includes('Invalid login credentials')) msg = 'Email ou senha incorretos.'
      if (msg.includes('User already registered')) msg = 'Este email já está cadastrado.'
      if (msg.includes('Email not confirmed')) msg = 'Email não confirmado. Verifique sua caixa de entrada.'
      
      setError(msg)
      toast.error(msg)
    } finally {
      setIsLoading(false)
    }
  }

  async function handleDemoLogin() {
    setIsLoading(true)
    setError(null)
    
    // Fixed credentials for Demo to avoid rate limits
    const demoEmail = 'demo@nexus.test'
    const demoPassword = 'DemoPassword123!'

    try {
      // 1. Try to Login first
      const { error: loginError } = await supabase.auth.signInWithPassword({
        email: demoEmail,
        password: demoPassword,
      })

      if (!loginError) {
        toast.success('Modo Demo ativado!')
        router.refresh()
        router.push('/dashboard')
        return
      }

      // 2. If Login fails, try to Signup
      if (loginError.message.includes('Invalid login credentials')) {
          const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
            email: demoEmail,
            password: demoPassword,
            options: {
              data: {
                full_name: 'Demo User',
              },
            },
          })

          if (!signUpError && signUpData.session) {
            toast.success('Conta Demo criada!')
            router.refresh()
            router.push('/dashboard')
            return
          }
      }

      // 3. Fallback: Anonymous Login (if enabled in Supabase)
      // If the above failed (e.g. rate limit, email confirmation required, or other error)
      const { error: anonError } = await supabase.auth.signInAnonymously()
      
      if (!anonError) {
        toast.success('Modo Demo (Anônimo) ativado!')
        router.refresh()
        router.push('/dashboard')
        return
      }

      // If everything fails, throw the original error
      throw loginError || anonError

    } catch (error: any) {
      console.error('Demo Auth error:', error)
      let msg = error.message
      if (msg.includes('rate limit')) msg = 'Muitas tentativas. Aguarde um momento ou use login normal.'
      
      setError(`Erro no Modo Demo: ${msg}`)
      toast.error('Falha ao entrar no modo demo.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-4">
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <Alert variant={error.includes('verifique') ? "default" : "destructive"} className={error.includes('verifique') ? "border-green-500 text-green-700 bg-green-50" : ""}>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>{error.includes('verifique') ? "Sucesso" : "Erro"}</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="seu@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="password">Senha</Label>
        <Input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {type === 'login' ? 'Entrar' : 'Criar Conta'}
      </Button>
    </form>
    
    <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Ou continue como
          </span>
        </div>
      </div>
      
      <Button 
        variant="outline" 
        className="w-full bg-green-50 text-green-700 hover:bg-green-100 hover:text-green-800 border-green-200" 
        onClick={handleDemoLogin}
        disabled={isLoading}
        type="button"
      >
        🧑‍💻 Entrar como Desenvolvedor (Sem Email)
      </Button>
    </div>
  )
}
