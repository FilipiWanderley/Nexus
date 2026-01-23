'use client'

import { useState, useEffect } from "react"
import { fetchWithAuth, getSessionId, optimizeResume } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Loader2, AlertCircle, CheckCircle2, XCircle, Upload, Download, FileText, Wand2, Copy } from "lucide-react"
import { jsPDF } from "jspdf"
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
  suggestions?: string[]
}

interface Resume {
  id: string
  user_id: string
  file_name: string
  file_path: string
  created_at: string
  raw_text?: string // Added raw_text
}

export default function DashboardView() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [selectedResumeId, setSelectedResumeId] = useState<string>("")
  const [jobDescription, setJobDescription] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ATSScoreResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [optimizing, setOptimizing] = useState(false)
  const [optimizedText, setOptimizedText] = useState("")
  
  // Upload State
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isDownloading, setIsDownloading] = useState<string | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

  useEffect(() => {
    loadResumes()
  }, [])

  const loadResumes = async () => {
    try {
      const data = await fetchWithAuth("/resumes/")
      if (Array.isArray(data)) {
        setResumes(data)
        if (data.length > 0 && !selectedResumeId) {
          setSelectedResumeId(data[0].id)
        }
      } else {
        setResumes([])
      }
    } catch (err) {
      console.error("Failed to load resumes", err)
      // toast.error("Failed to load resumes") // Suppress error on initial load if auth is tricky
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
      // Use fetchWithAuth wrapper which handles Session ID correctly
      // Note: We need to pass FormData, and fetchWithAuth will handle headers
      const formData = new FormData()
      formData.append('file', uploadFile)

      const data = await fetchWithAuth("/resumes/upload_resume", {
        method: "POST",
        body: formData
      })
      
      // Guest mode: Resume is not saved in DB list, but we get it back in response
      // Add it to local state so user can select it
      if (!data || !data.id) {
        throw new Error("Resposta inválida do servidor. Tente novamente.")
      }

      const newResume = data as Resume
      setResumes(prev => [newResume, ...prev])
      setSelectedResumeId(newResume.id)
      
      toast.success("Currículo enviado com sucesso!")
      setUploadFile(null)
      
      // Reset file input
      const fileInput = document.getElementById('resume-upload') as HTMLInputElement
      if (fileInput) fileInput.value = ''
      
    } catch (err: any) {
      console.error("Upload error:", err)
      toast.error(`Erro no envio: ${err.message}`)
    } finally {
      setIsUploading(false)
    }
  }

  const handleDownload = async (fileName: string) => {
    setIsDownloading(fileName)
    try {
      const sessionId = getSessionId()
      const response = await fetch(`${API_URL}/resumes/download_resume?file_name=${encodeURIComponent(fileName)}`, {
        method: 'GET',
        headers: {
          'X-Session-ID': sessionId,
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
      const selectedResume = resumes.find(r => r.id === selectedResumeId)
      
      const bodyPayload: any = {
        job_description: jobDescription
      }
      
      if (selectedResume?.raw_text) {
        // Use stateless mode if text is available (guest mode)
        bodyPayload.resume_text = selectedResume.raw_text
        // We still send resume_id just in case, or we can omit it if backend allows
        bodyPayload.resume_id = selectedResumeId
      } else {
         // Legacy/DB mode
         bodyPayload.resume_id = selectedResumeId
      }

      const data = await fetchWithAuth("/analysis/score", {
        method: "POST",
        body: JSON.stringify(bodyPayload)
      })
      setResult(data)
    } catch (err: any) {
      setError(err.message || "Falha ao analisar o currículo")
    } finally {
      setLoading(false)
    }
  }

  const handleOptimize = async () => {
    if (!result || !selectedResumeId || !jobDescription) return
    
    setOptimizing(true)
    setError(null)
    try {
        const selectedResume = resumes.find(r => r.id === selectedResumeId)
        const resumeText = selectedResume?.raw_text

        const data = await optimizeResume(
            selectedResumeId,
            jobDescription,
            result.missing_critical_skills,
            result.missing_bonus_skills,
            result.suggestions || [],
            resumeText // Pass the raw text if available
        )
        setOptimizedText(data.optimized_resume_text)
        toast.success("Currículo otimizado gerado com sucesso!")
        
        // Scroll to bottom
        setTimeout(() => {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
        }, 100)
        
    } catch (e: any) {
        console.error(e)
        setError(e.message || "Falha ao gerar currículo otimizado")
        toast.error("Falha ao gerar currículo otimizado")
    } finally {
        setOptimizing(false)
    }
  }

  const copyToClipboard = () => {
    if (optimizedText) {
      navigator.clipboard.writeText(optimizedText)
      toast.success("Currículo copiado para a área de transferência!")
    }
  }

  const handleDownloadPDF = () => {
    if (!optimizedText) return

    const doc = new jsPDF()
    
    // Configurações da página
    const pageWidth = doc.internal.pageSize.getWidth()
    const pageHeight = doc.internal.pageSize.getHeight()
    const margin = 20
    const maxLineWidth = pageWidth - (margin * 2)
    const lineHeight = 7
    
    // Título do Documento
    doc.setFontSize(18)
    doc.setFont('helvetica', 'bold')
    doc.text('Currículo Otimizado', margin, margin)
    
    let cursorY = margin + 15

    // Função auxiliar para limpar markdown e adicionar nova página se necessário
    const checkPageBreak = (heightNeeded: number = lineHeight) => {
      if (cursorY + heightNeeded > pageHeight - margin) {
        doc.addPage()
        cursorY = margin
      }
    }

    // Processa o texto linha por linha para tratar o Markdown básico
    const lines = optimizedText.split('\n')

    lines.forEach((line) => {
      let text = line.trim()
      if (!text) {
        cursorY += lineHeight / 2 // Espaço menor para linhas vazias
        return
      }

      // 1. Tratamento de Títulos (Markdown #, ##, ###)
      if (text.startsWith('#')) {
        checkPageBreak(10)
        
        let fontSize = 12
        if (text.startsWith('###')) {
          fontSize = 13
          text = text.replace(/^###\s*/, '')
        } else if (text.startsWith('##')) {
          fontSize = 14
          text = text.replace(/^##\s*/, '')
          cursorY += 5 // Espaço extra antes de seções principais
        } else if (text.startsWith('#')) {
          fontSize = 16
          text = text.replace(/^#\s*/, '')
          cursorY += 8
        }

        // Remove negrito do markdown (**texto**) para o título, pois já será negrito
        text = text.replace(/\*\*/g, '')

        doc.setFont('helvetica', 'bold')
        doc.setFontSize(fontSize)
        doc.text(text, margin, cursorY)
        cursorY += lineHeight + 2
        
        // Retorna para fonte normal
        doc.setFont('helvetica', 'normal')
        doc.setFontSize(11)
        return
      }

      // 2. Tratamento de Listas (Markdown * ou -)
      if (text.startsWith('* ') || text.startsWith('- ')) {
        text = text.replace(/^[\*\-]\s*/, '') // Remove o marcador original
        
        // Remove negrito simples do corpo da lista para ficar limpo
        // (O jsPDF básico não suporta rich text inline facilmente)
        text = text.replace(/\*\*/g, '') 

        const bulletIndent = 5
        const bulletText = `•  ${text}`
        
        // Quebra o texto da lista para caber na margem
        const splitBullet = doc.splitTextToSize(bulletText, maxLineWidth - bulletIndent)
        
        checkPageBreak(splitBullet.length * lineHeight)

        doc.setFont('helvetica', 'normal')
        doc.setFontSize(11)
        
        splitBullet.forEach((line: string) => {
          doc.text(line, margin + bulletIndent, cursorY)
          cursorY += lineHeight
        })
        return
      }

      // 3. Texto Normal
      // Remove negrito simples (**texto**) para limpar a visualização
      text = text.replace(/\*\*/g, '')
      
      const splitText = doc.splitTextToSize(text, maxLineWidth)
      checkPageBreak(splitText.length * lineHeight)
      
      doc.setFont('helvetica', 'normal')
      doc.setFontSize(11)
      doc.text(splitText, margin, cursorY)
      cursorY += splitText.length * lineHeight
    })
    
    doc.save('curriculo-otimizado-nexus.pdf')
    toast.success("PDF formatado baixado com sucesso!")
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
          <h1 className="text-3xl font-bold tracking-tight">Análise de Currículo</h1>
          <p className="text-muted-foreground mt-2">
            Faça upload do seu currículo e analise-o contra descrições de vagas.
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
                <CardDescription>Envie um currículo em PDF.</CardDescription>
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
                        Selecione um arquivo PDF para habilitar o botão.
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
                    {resumes.map((resume) => {
                      if (!resume || !resume.id) return null;
                      return (
                      <div 
                        key={resume.id} 
                        className={`flex items-center justify-between p-3 border rounded-lg cursor-pointer transition-colors ${
                          selectedResumeId === resume.id ? "bg-accent border-primary" : "bg-card hover:bg-accent/50"
                        }`}
                        onClick={() => setSelectedResumeId(resume.id)}
                      >
                        <div className="flex items-center gap-3 overflow-hidden">
                          <FileText className="h-8 w-8 text-primary/80 shrink-0" />
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate" title={resume.file_name}>
                              {resume.file_name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {resume.created_at ? new Date(resume.created_at).toLocaleDateString() : 'Data desconhecida'}
                            </p>
                          </div>
                        </div>
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDownload(resume.file_name);
                          }}
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
                    )})}
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

                {result.suggestions && result.suggestions.length > 0 && (
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                    <h4 className="font-semibold mb-3 text-blue-800 flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      Sugestões de Melhoria
                    </h4>
                    <ul className="space-y-2">
                      {result.suggestions.map((suggestion, index) => (
                        <li key={index} className="flex items-start gap-2 text-blue-700">
                          <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-blue-500 flex-shrink-0" />
                          <span>{suggestion}</span>
                        </li>
                      ))}
                    </ul>
                    
                    <div className="mt-6 pt-4 border-t border-blue-200">
                         <Button 
                             onClick={handleOptimize} 
                             disabled={optimizing} 
                             className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                         >
                             {optimizing ? (
                                 <>
                                     <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                     Gerando Currículo Otimizado...
                                 </>
                             ) : (
                                 <>
                                     <Wand2 className="mr-2 h-4 w-4" />
                                     Gerar Currículo Otimizado (Versão Final)
                                 </>
                             )}
                         </Button>
                         <p className="text-xs text-blue-600 mt-2 text-center">
                             Gera um currículo completo e reescrito integrando todas as sugestões e palavras-chave.
                         </p>
                    </div>
                  </div>
                )}

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

                {optimizedText && (
                    <Card className="border-green-200 bg-green-50/30 overflow-hidden">
                        <div className="bg-green-600">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2 text-white">
                                    <CheckCircle2 className="h-5 w-5 text-white" />
                                    Currículo Otimizado Gerado
                                </CardTitle>
                                <CardDescription className="text-green-100">
                                    Copie o texto abaixo e use como seu novo currículo. Ele foi adaptado para passar no ATS desta vaga.
                                </CardDescription>
                            </CardHeader>
                        </div>
                        <CardContent className="mt-6">
                            <div className="relative">
                                <Textarea 
                                    value={optimizedText} 
                                    readOnly 
                                    className="min-h-[500px] font-mono text-sm bg-white text-black border-gray-200 focus-visible:ring-0"
                                />
                                <Button
                                    size="sm"
                                    className="absolute top-2 right-24 bg-red-600 hover:bg-red-700 text-white border-none shadow-sm"
                                    onClick={handleDownloadPDF}
                                >
                                    <Download className="h-4 w-4 mr-2" />
                                    Baixar PDF
                                </Button>
                                <Button
                                    size="sm"
                                    className="absolute top-2 right-2 bg-black hover:bg-gray-800 text-white border-none shadow-sm"
                                    onClick={copyToClipboard}
                                >
                                    <Copy className="h-4 w-4 mr-2" />
                                    Copiar
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                )}
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