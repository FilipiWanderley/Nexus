'use client'

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/utils/supabase/client"
import { fetchWithAuth } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Loader2, AlertCircle, CheckCircle2, XCircle, Upload, Download, FileText, Trash2 } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { toast } from "sonner"

// Types
interface ScoreBreakdown {
  keyword_score: number
  semantic_score: number
  seniority_score: number
  penalties: number
}

interface ATSScoreResult {
  final_score: number
  breakdown: ScoreBreakdown
  missing_critical_skills: string[]
  missing_bonus_skills: string[]
  explanation: string
}

interface Resume {
  id: string
  user_id: string
  file_name: string
  file_path: string
  created_at: string
}

export default function DashboardPage() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [selectedResumeId, setSelectedResumeId] = useState<string>("")
  const [jobDescription, setJobDescription] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ATSScoreResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Upload State
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isDownloading, setIsDownloading] = useState<string | null>(null)

  const supabase = createClient()
  const router = useRouter()
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

  useEffect(() => {
    loadResumes()
  }, [])

  const loadResumes = async () => {
    try {
      const data = await fetchWithAuth("/resumes/")
      setResumes(data)
      if (data.length > 0 && !selectedResumeId) {
        setSelectedResumeId(data[0].id)
      }
    } catch (err) {
      console.error("Failed to load resumes", err)
      toast.error("Failed to load resumes")
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUploadFile(e.target.files[0])
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!uploadFile) return

    setIsUploading(true)
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) throw new Error('Not authenticated')

      const formData = new FormData()
      formData.append('file', uploadFile)

      const response = await fetch(`${API_URL}/resumes/upload_resume`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Upload failed')
      }

      toast.success('Resume uploaded successfully!')
      setUploadFile(null)
      // Reset file input by ID if needed, but simple state reset is often enough for React logic
      // though the native input holds the value. 
      const fileInput = document.getElementById('resume-upload') as HTMLInputElement
      if (fileInput) fileInput.value = ''
      
      await loadResumes()
    } catch (error: any) {
      console.error('Upload error:', error)
      toast.error(error.message)
    } finally {
      setIsUploading(false)
    }
  }

  const handleDownload = async (fileName: string) => {
    setIsDownloading(fileName)
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) throw new Error('Not authenticated')

      const response = await fetch(`${API_URL}/resumes/download_resume?file_name=${encodeURIComponent(fileName)}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
      })

      if (!response.ok) {
        if (response.status === 404) throw new Error('File not found')
        throw new Error('Download failed')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = fileName
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast.success('Download started')
    } catch (error: any) {
      console.error('Download error:', error)
      toast.error(error.message)
    } finally {
      setIsDownloading(null)
    }
  }

  const handleAnalyze = async () => {
    if (!selectedResumeId || !jobDescription) {
      setError("Por favor, selecione um currículo e insira a descrição da vaga")
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await fetchWithAuth("/analysis/score", {
        method: "POST",
        body: JSON.stringify({
          resume_id: selectedResumeId,
          job_description: jobDescription
        })
      })
      setResult(data)
    } catch (err: any) {
      setError(err.message || "Falha ao analisar o currículo")
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  return (
    <div className="container mx-auto py-10 px-4 max-w-6xl">
      <div className="flex flex-col gap-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Painel de Controle</h1>
          <p className="text-muted-foreground mt-2">
            Gerencie seus currículos e otimize-os para candidaturas de emprego.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-12">
          {/* Left Column: Resume Management (4 cols) */}
          <div className="md:col-span-4 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Enviar Currículo
                </CardTitle>
                <CardDescription>Envie um currículo em PDF para sua biblioteca.</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleUpload} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="resume-upload">Arquivo PDF</Label>
                    <Input 
                      id="resume-upload" 
                      type="file" 
                      accept=".pdf" 
                      onChange={handleFileChange}
                      disabled={isUploading}
                      className="cursor-pointer"
                    />
                    {!uploadFile && (
                      <p className="text-xs text-muted-foreground">
                        Selecione um arquivo PDF para habilitar o botão de envio.
                      </p>
                    )}
                  </div>
                  <Button type="submit" className="w-full" disabled={!uploadFile || isUploading}>
                    {isUploading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Enviando...
                      </>
                    ) : (
                      'Enviar Currículo'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Seus Currículos
                </CardTitle>
                <CardDescription>Gerencie seus currículos enviados.</CardDescription>
              </CardHeader>
              <CardContent>
                {resumes.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">Nenhum currículo enviado ainda.</p>
                ) : (
                  <div className="space-y-3">
                    {resumes.map((resume) => (
                      <div key={resume.id} className="flex items-center justify-between p-3 border rounded-lg bg-card hover:bg-accent/50 transition-colors">
                        <div className="flex items-center gap-3 overflow-hidden">
                          <FileText className="h-8 w-8 text-primary/80 shrink-0" />
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate" title={resume.file_name}>
                              {resume.file_name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {new Date(resume.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={() => handleDownload(resume.file_name)}
                          disabled={isDownloading === resume.file_name}
                          title="Baixar"
                        >
                          {isDownloading === resume.file_name ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Download className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Column: ATS Analysis (8 cols) */}
          <div className="md:col-span-8 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Análise ATS</CardTitle>
                <CardDescription>Analise seu currículo contra uma descrição de vaga.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="resume-select">Selecionar Currículo</Label>
                  <select 
                    id="resume-select"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    value={selectedResumeId}
                    onChange={(e) => setSelectedResumeId(e.target.value)}
                    disabled={resumes.length === 0}
                  >
                    <option value="" disabled>Selecione um currículo...</option>
                    {resumes.map((resume) => (
                      <option key={resume.id} value={resume.id}>
                        {resume.file_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="jd-input">Descrição da Vaga</Label>
                  <Textarea 
                    id="jd-input"
                    placeholder="Cole a descrição completa da vaga aqui..."
                    className="min-h-[150px]"
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                  />
                </div>

                {error && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Erro</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
              </CardContent>
              <CardFooter>
                <Button 
                  onClick={handleAnalyze} 
                  disabled={loading || !selectedResumeId || !jobDescription} 
                  className="w-full"
                >
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {loading ? "Analisando..." : "Calcular Pontuação ATS"}
                </Button>
              </CardFooter>
            </Card>

            {/* Analysis Results */}
            {result ? (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <Card>
                  <CardHeader>
                    <CardTitle>Pontuação de Compatibilidade</CardTitle>
                    <CardDescription>Compatibilidade geral com esta função</CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-col items-center justify-center py-6">
                    <div className="relative flex items-center justify-center">
                      <div className={`text-6xl font-bold ${getScoreColor(result.final_score)}`}>
                        {result.final_score}
                      </div>
                      <span className="text-2xl text-muted-foreground ml-1">/100</span>
                    </div>
                    <p className="mt-4 text-center text-muted-foreground px-4">
                      {result.explanation}
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Detalhamento</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Palavras-chave (40%)</span>
                        <span className="font-medium">{result.breakdown.keyword_score.toFixed(0)}/100</span>
                      </div>
                      <Progress value={result.breakdown.keyword_score} className="h-2" />
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Similaridade Semântica (40%)</span>
                        <span className="font-medium">{result.breakdown.semantic_score.toFixed(0)}/100</span>
                      </div>
                      <Progress value={result.breakdown.semantic_score} className="h-2" />
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Adequação de Senioridade (20%)</span>
                        <span className="font-medium">{result.breakdown.seniority_score.toFixed(0)}/100</span>
                      </div>
                      <Progress value={result.breakdown.seniority_score} className="h-2" />
                    </div>
                    
                    {result.breakdown.penalties > 0 && (
                       <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-2 rounded mt-2">
                          <AlertCircle className="h-4 w-4" />
                          <span>Penalidade Aplicada: -{result.breakdown.penalties} pontos (Habilidades Críticas Ausentes ou Formatação)</span>
                       </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Análise de Lacunas</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                        <XCircle className="h-4 w-4 text-red-500" /> Habilidades Críticas Ausentes
                      </h4>
                      {result.missing_critical_skills.length === 0 ? (
                        <p className="text-sm text-muted-foreground italic">Nenhuma! Ótimo trabalho.</p>
                      ) : (
                        <div className="flex flex-wrap gap-2">
                          {result.missing_critical_skills.map((skill) => (
                            <Badge key={skill} variant="destructive">{skill}</Badge>
                          ))}
                        </div>
                      )}
                    </div>

                    <div>
                      <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                        <AlertCircle className="h-4 w-4 text-yellow-500" /> Habilidades Bônus Ausentes
                      </h4>
                      {result.missing_bonus_skills.length === 0 ? (
                        <p className="text-sm text-muted-foreground italic">Nenhuma.</p>
                      ) : (
                        <div className="flex flex-wrap gap-2">
                          {result.missing_bonus_skills.map((skill) => (
                            <Badge key={skill} variant="secondary">{skill}</Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card className="h-full flex items-center justify-center bg-muted/50 border-dashed min-h-[300px]">
                <CardContent className="text-center py-10">
                  <div className="text-muted-foreground">
                    <p className="text-lg font-medium">Pronto para Analisar</p>
                    <p className="text-sm">Selecione um currículo e cole a descrição da vaga para ver sua pontuação.</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
