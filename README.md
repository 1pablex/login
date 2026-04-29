# 🚀 Sistema de Login 1.0

Sistema de login com autenticação, criptografia de senha, recuperação de senha via e-mail e integração com banco de dados.

---

## 📌 Tecnologias utilizadas

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Bcrypt
* Flask-Talisman
* SQLite
* Brevo (envio de e-mail)

---

## ⚙️ Como rodar o projeto

### 🔽 1. Clonar o repositório

```bash
git clone https://github.com/1pablex/login
cd login
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
SECRET_KEY=suasecretkey
DATABASE_URL=sqlite:///usuarios.db
BREVO_API_KEY=sua-chave-aqui
BREVO_SENDER_EMAIL=exemplo@dominio.com
BREVO_SENDER_NAME=Suporte
```

---

### ▶️ 6. Rodar o projeto

```bash
python app.py
```

---

## 🔐 Funcionalidades

* Cadastro de usuários com e-mail e senha criptografada
* Login com autenticação por sessão
* Recuperação de senha via e-mail (Brevo)
* Redefinição de senha com token seguro (expira em 1 hora)
* Headers de segurança HTTP via Flask-Talisman (CSP, X-Frame-Options, HSTS)
* Perfis: Psicólogo e Paciente
