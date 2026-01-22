import Link from "next/link"
import { AuthForm } from "@/components/auth/auth-form"

export default function LoginPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-zinc-50 dark:bg-zinc-950">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            Entrar no Nexus
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Ou{" "}
            <Link
              href="/signup"
              className="font-medium text-primary hover:text-primary/90"
            >
              criar uma nova conta
            </Link>
          </p>
        </div>
        <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
          <AuthForm type="login" />
        </div>
      </div>
    </div>
  )
}
