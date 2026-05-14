# 🚀 Sistema de Login 1.1

Sistema de autenticação segura para ambiente clínico psicológico, com múltiplas camadas de proteção, auditoria de eventos e conformidade com a LGPD.

---

## 📌 O que mudou na versão 1.1

- Migração do banco de dados de **SQLite** para **Firebase Firestore** (NoSQL, criptografado em repouso com AES-256)
- Implementação de **autenticação de dois fatores (2FA)** via e-mail
- Adicionado **rate limiting** — bloqueio após 5 tentativas de login por minuto
- Adicionado **Flask-Talisman** — headers de segurança HTTP (CSP, HSTS, X-Frame-Options)
- Sistema de **auditoria completo** — todos os eventos de segurança registrados no Firestore
- Funcionalidades **LGPD** — alteração e exclusão de dados pelo titular
- Refatoração da arquitetura seguindo padrão **MVC + SOLID**
- Separação em **services** por responsabilidade única

---

## 📌 Tecnologias utilizadas

- Python 3.12
- Flask 3.1.3
- Flask-Bcrypt
- Flask-Talisman
- Flask-Limiter
- Firebase Firestore (banco de dados NoSQL)
- firebase-admin
- Brevo REST API (envio de e-mail)
- gunicorn (produção)

---

## ⚙️ Como rodar o projeto

### 🔽 1. Clonar o repositório

```bash
git clone https://github.com/1pablex/login
cd login
git checkout login-1.1
```

---

### 🐍 2. Criar ambiente virtual

```bash
python -m venv venv
```

---

### ▶️ 3. Ativar o ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

---

### 📦 4. Instalar dependências

```bash
pip install -r requirements.txt
```

---

### 🔑 5. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
SECRET_KEY=sua-secretkey
BREVO_API_KEY=xkeysib-sua-chave-aqui
BREVO_SENDER_EMAIL=exemplo@seudominio.com
BREVO_SENDER_NAME=Suporte
FIREBASE_CREDENTIALS=seu-arquivo-firebase.json
```

> ⚠️ O arquivo `.json` de credenciais do Firebase nunca deve ser enviado ao GitHub — adicione-o ao `.gitignore`.

---

### 🔥 6. Configurar Firebase

1. Acesse [console.firebase.google.com](https://console.firebase.google.com)
2. Crie um projeto e ative o **Firestore Database**
3. Vá em **Configurações → Contas de serviço → Gerar nova chave privada**
4. Salve o arquivo `.json` na raiz do projeto
5. Adicione o nome do arquivo no `.env` como `FIREBASE_CREDENTIALS`

---

### ▶️ 7. Rodar o projeto

```bash
python app.py
```

---

## 🔐 Funcionalidades

- Cadastro de usuários com e-mail e senha criptografada (bcrypt fator 12)
- Login com autenticação por sessão
- Autenticação de dois fatores (2FA) via e-mail — código expira em 10 minutos
- Proteção contra força bruta — bloqueio após 5 tentativas/minuto por IP
- Recuperação de senha via e-mail (Brevo)
- Redefinição de senha com token seguro (expira em 1 hora)
- Headers de segurança HTTP via Flask-Talisman
- Auditoria completa de eventos de segurança no Firestore
- Alteração de dados do usuário (LGPD Art. 18, III)
- Exclusão de conta pelo titular (LGPD Art. 18, VI)
- Perfis: Psicólogo e Paciente

---

## 🏗️ Arquitetura

```
login/
├── app.py                        ← Controller (rotas HTTP)
├── database.py                   ← Conexão com Firebase
├── models.py                     ← Estrutura dos dados
├── repositories/
│   └── usuario_repository.py     ← Acesso ao Firestore
├── services/
│   ├── autenticacao.py           ← Validação e sessão
│   ├── email_service.py          ← E-mails via Brevo
│   ├── auditoria.py              ← Registro de eventos
│   ├── perfil_service.py         ← Atualização de dados (LGPD)
│   └── exclusao_service.py       ← Exclusão de conta (LGPD)
├── templates/                    ← Interface HTML
├── static/                       ← CSS
├── .env                          ← Variáveis de ambiente
└── requirements.txt
```
