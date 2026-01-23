# Nexus Career AI


## 📋 Visão Geral

**Nexus Career AI** é um Otimizador de Currículos ATS (Application Tracking System) SaaS de alto nível, projetado para profissionais de tecnologia. Ele utiliza IA avançada (Google Gemini) para analisar currículos em relação a descrições de vagas, calcular pontuações de compatibilidade ATS e gerar currículos totalmente otimizados e reescritos em segundos.

![Status](https://img.shields.io/badge/Status-Desenvolvimento_Ativo-green)
![Tech Stack](https://img.shields.io/badge/Stack-Next.js_|_FastAPI_|_Supabase_|_Gemini-blue)

---

## ✨ Principais Funcionalidades

- **📊 Sistema de Pontuação ATS:** Calcula instantaneamente o quanto um currículo corresponde a uma vaga específica com base em palavras-chave, senioridade e similaridade semântica.
- **🪄 Otimização de Currículo em 1 Clique:** Gera uma versão completa e reescrita do currículo que integra naturalmente as habilidades ausentes e melhora os pontos (bullet points) para máximo impacto.
- **📄 Exportação para PDF:** Baixe o currículo otimizado formatado profissionalmente em PDF, com layout limpo, listas organizadas e destaque visual para seções importantes.
- **🌍 Suporte Multilíngue (PT-BR):** Todas as análises, feedbacks e sugestões são fornecidos em Português, adaptados ao mercado brasileiro.
- **👤 Modo Convidado (Sem Login):** Usuários podem enviar currículos, analisá-los e baixar versões otimizadas sem a necessidade de criar uma conta.
- **⚡ Análise em Tempo Real:** Ciclo de feedback rápido usando modelos de IA de alta performance (Gemini Pro/Flash).
- **🔒 Arquitetura Segura:** Clara separação de responsabilidades com um backend seguro e sessões de convidado efêmeras.

---

## 🏗️ Arquitetura

O Nexus Career AI segue uma **Arquitetura Orientada a Serviços (SOA)**, desacoplando a experiência do usuário no frontend do motor de inteligência no backend.

```mermaid
graph TD
    User[Usuário (Navegador)] -->|HTTPS| Frontend[Frontend (Next.js 15)]
    
    subgraph "Camada Cliente"
        Frontend -->|Requisições API| Backend[Backend API (FastAPI)]
        Frontend -->|Uploads de Arquivos (Convidado)| Backend
    end

    subgraph "Camada Backend (Python)"
        Backend -->|Orquestração| ServiceLayer[Serviços]
        ServiceLayer -->|Inferência IA| AI[Gemini AI]
        ServiceLayer -->|Persistência de Dados| DB[(Supabase PostgreSQL)]
        ServiceLayer -->|Armazenamento de Arquivos| Storage[Supabase Storage]
    end
```

### Componentes Principais

1.  **Frontend (Next.js 15 + Tailwind CSS):**
    *   Gerencia a interação do usuário, uploads de arquivos e visualização do dashboard.
    *   Gerencia "Sessões de Convidado" usando armazenamento local e IDs temporários.
    *   Exibe resultados de análise em tempo real (Pontuação, Lacunas, Sugestões).

2.  **Backend (Python FastAPI):**
    *   **API Gateway:** Expõe endpoints RESTful para análise e otimização.
    *   **Serviço de Currículo:** Lida com validação de arquivos, upload e extração de texto (PDF).
    *   **Motor ATS:** Calcula pontuações de compatibilidade usando frequência de palavras-chave e análise semântica.
    *   **Serviço de IA:** Interface com o Google Gemini para gerar reescritas de currículo humanizadas.

3.  **Infraestrutura (Supabase):**
    *   **Banco de Dados:** PostgreSQL para armazenar dados estruturados (opcional para convidados).
    *   **Storage:** Armazenamento de objetos para arquivos PDF.

---

## 🚀 Implantação (Vercel)

Este projeto utiliza uma estrutura monorepo com diretórios separados para `frontend` e `backend`. 

**Para implantação no Vercel:**
1. Configure o **Root Directory** nas configurações do projeto para `frontend`.
2. Assegure-se de que as variáveis de ambiente (`NEXT_PUBLIC_API_URL`, etc.) estejam configuradas.
3. **Nota:** O projeto utiliza `src/proxy.ts` (Next.js 16+) em vez de `middleware.ts`. O Vercel deve detectar isso automaticamente.
4. Se houver erros de build, verifique os logs mais recentes.

---

## 🛠️ Tecnologias Utilizadas

### Frontend
- **Framework:** Next.js 15 (App Router)
- **Linguagem:** TypeScript
- **Estilização:** Tailwind CSS + Shadcn/ui
- **Gerenciamento de Estado:** React Hooks
- **Ícones:** Lucide React

### Backend
- **Framework:** FastAPI (Python 3.9+)
- **Modelo de IA:** Google Gemini (Gemini Pro / 1.5 Flash)
- **Processamento de PDF:** PyPDF2
- **Validação:** Pydantic
- **Cliente de Banco de Dados:** Supabase-py

---

## 📂 Estrutura do Projeto

```bash
Nexus/
├── backend/                 # Aplicação FastAPI
│   ├── app/
│   │   ├── api/             # Manipuladores de Rotas da API
│   │   ├── core/            # Configuração, Segurança, Logs
│   │   ├── schemas/         # Modelos Pydantic (Requisição/Resposta)
│   │   ├── services/        # Lógica de Negócios (IA, Currículo, ATS)
│   │   └── clients/         # Clientes Externos (Gemini, Supabase)
│   ├── venv/                # Ambiente Virtual
│   └── main.py              # Ponto de Entrada da Aplicação
│
├── frontend/                # Aplicação Next.js
│   ├── src/
│   │   ├── app/             # Páginas do App Router
│   │   ├── components/      # Componentes de UI (Dashboard, Cards)
│   │   └── lib/             # Utilitários de API e Helpers
│   ├── public/              # Ativos Estáticos
│   └── next.config.ts       # Configuração do Next.js
│
└── README.md                # Documentação do Projeto
```

---

## 🚀 Como Iniciar

### Pré-requisitos
- Node.js (v18+)
- Python (v3.9+)
- Conta no Supabase (para Banco de Dados e Storage)
- Chave do Google AI Studio (para Gemini)

### 1. Configuração do Backend

```bash
cd backend

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar Ambiente
# Crie um arquivo .env com:
# GOOGLE_API_KEY=sua_chave_gemini
# SUPABASE_URL=sua_url_supabase
# SUPABASE_KEY=sua_chave_anon_supabase

# Rodar o Servidor
python3 -m uvicorn app.main:app --reload
```
*O Backend roda em `http://localhost:8000`*

### 2. Configuração do Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar Ambiente
# Crie um arquivo .env.local com:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Rodar o Servidor de Desenvolvimento
npm run dev
```
*O Frontend roda em `http://localhost:3000`*

---

## 📡 Documentação da API

Principais endpoints disponíveis no backend:

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/resumes/upload_resume` | Envia um currículo em PDF (Suporta convidados). |
| `POST` | `/analysis/score` | Calcula a pontuação ATS contra uma Descrição de Vaga. |
| `POST` | `/analysis/optimize` | Gera um texto completo de currículo reescrito. |
| `GET` | `/resumes/download_resume` | Baixa o arquivo de currículo armazenado. |

---

## 📜 Licença

Este projeto é proprietário e desenvolvido para fins de demonstração de portfólio.
