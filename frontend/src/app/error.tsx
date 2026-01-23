'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Runtime Error caught by Error Boundary:', error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center space-y-4">
      <h2 className="text-2xl font-bold text-red-600">Algo deu errado!</h2>
      <p className="text-muted-foreground max-w-md">
        Ocorreu um erro inesperado na aplicação. Tente recarregar a página.
      </p>
      <div className="p-4 bg-gray-100 rounded-md text-left text-xs font-mono overflow-auto max-w-full max-h-48 w-full">
        {error.message}
      </div>
      <div className="flex gap-4">
        <Button onClick={() => window.location.reload()}>
          Recarregar Página
        </Button>
        <Button variant="outline" onClick={() => reset()}>
          Tentar Novamente
        </Button>
      </div>
    </div>
  )
}
