'use client'

import DashboardView from '@/components/dashboard/dashboard-view'

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <header className="px-6 h-16 flex items-center justify-between border-b border-border">
        <div className="flex items-center gap-2 font-bold text-xl">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white">
            N
          </div>
          Nexus Career AI
        </div>
        <div className="text-sm text-muted-foreground">
           Modo Aberto (No Login)
        </div>
      </header>
      <DashboardView />
    </main>
  )
}
