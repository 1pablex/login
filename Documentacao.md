# Sistema de Login do TEAcare 1.0 — Documentação Técnica de Segurança

**Autores:** Pablo de Souza Santos · Matheus Henrique Silva Oliveira  
**Data:** Abril de 2026

---

## 1. Visão Geral do Sistema

O Sistema de Login do TEAcare 1.0 é uma aplicação web desenvolvida em Python com o framework Flask, voltada para o gerenciamento seguro de autenticação de usuários em um contexto clínico psicológico. O sistema contempla dois perfis de usuário — **Psicólogo** e **Paciente** — e implementa mecanismos de segurança alinhados às melhores práticas de desenvolvimento seguro.

### 1.1 Tecnologias Utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python + Flask | 3.12 / 3.1.3 | Framework web |
| Flask-SQLAlchemy | 3.1.1 | ORM para banco de dados |
| Flask-Bcrypt | 1.0.1 | Hashing seguro de senhas |
| Flask-Talisman | 1.1.0 | Headers de segurança HTTP |
| SQLite | — | Banco de dados relacional |
| Brevo REST API | — | Envio de e-mails transacionais |
| python-dotenv | — | Gerenciamento de variáveis de ambiente |

### 1.2 Arquitetura do Sistema

O sistema segue o padrão **MVC (Model-View-Controller)** com separação em camadas:

- `models.py` — definição das entidades `Usuario` e `Role`
- `repositories/` — acesso ao banco de dados (`usuario_repository.py`)
- `services/` — lógica de negócio (`email_service.py`, `autenticacao.py`)
- `templates/` — interface HTML (Jinja2)
- `app.py` — rotas e controladores Flask

---

## 2. Autenticação e Gestão de Credenciais

### 2.1 Hash Criptográfico de Senhas

O sistema utiliza o algoritmo **bcrypt** para armazenamento seguro de senhas. O bcrypt foi escolhido por incorporar nativamente um salt aleatório por usuário e por ser resistente a ataques de força bruta devido ao seu fator de custo adaptável.

#### Implementação

A biblioteca Flask-Bcrypt (versão 1.0.1) encapsula o bcrypt com **fator de custo padrão de 12 rounds**, gerando hashes no formato `$2b$12$...`, onde:

- `$2b$` — versão do algoritmo bcrypt
- `$12$` — fator de custo (2¹² = 4.096 iterações)
- Próximos 22 caracteres — salt aleatório gerado automaticamente
- Caracteres restantes — hash da senha

#### Justificativa Técnica

O fator de custo 12 representa um equilíbrio entre segurança e desempenho: é suficientemente lento para dificultar ataques de força bruta (~300ms por hash), mas rápido o suficiente para não prejudicar a experiência do usuário.

### 2.2 Autenticação de Dois Fatores (2FA)

O sistema implementa autenticação de dois fatores via e-mail. Após validação das credenciais primárias, um código numérico de **6 dígitos** é gerado e enviado ao e-mail cadastrado do usuário.

#### Fluxo de Autenticação

1. Usuário insere nome de usuário e senha
2. Sistema valida as credenciais com `bcrypt.check_password_hash()`
3. Se válidas, gera código de 6 dígitos via `random.randint()` com expiração de **10 minutos**
4. Código é armazenado em `codigo_2fa` e `codigo_2fa_expiry` no banco
5. Usuário é redirecionado para `/verificar-2fa`
6. Após inserir o código correto, a sessão é completamente iniciada
7. Código é invalidado após uso (campos zerados no banco)

### 2.3 Gestão de Sessões

As sessões são gerenciadas pelo mecanismo nativo do Flask, utilizando cookies assinados com a `SECRET_KEY` definida em variável de ambiente. A sessão é completamente limpa no logout via `session.clear()`.

### 2.4 Proteção Contra Força Bruta

O requisito de proteção contra força bruta é **parcialmente atendido** pelo custo computacional do bcrypt (fator 12), que torna cada tentativa de autenticação custosa para o atacante.

### 2.5 Tabela de Requisitos — Autenticação

| Nº | Requisito | Status |
|----|-----------|--------|
| 1.1 | Uso de hash criptográfico seguro (bcrypt) | ✅ Atendido |
| 1.2 | Parâmetros de custo configurados — fator 12 | ✅ Atendido |
| 1.3 | Salt criptográfico único por usuário | ✅ Atendido (bcrypt nativo) |
| 1.4 | Armazenamento correto do hash + salt | ✅ Atendido |
| 1.5 | Autenticação de dois fatores (2FA) | ✅ Atendido (e-mail) |
| 1.6 | Validação do 2FA após autenticação primária | ✅ Atendido |
| 1.7 | Fluxo de autenticação documentado | ✅ Este documento |
| 1.8 | Evidências funcionais | ✅ Prints incluídos |
| 1.9 | Sessões com tempo de expiração | ✅ Atendido |
| 1.10 | Invalidação de sessão no logout | ✅ `session.clear()` |
| 1.11 | Proteção contra força bruta | ⚠️ Parcial (custo bcrypt) |
| 1.12 | Justificativas técnicas documentadas | ✅ Este documento |

---

## 3. Recuperação de Senha

O sistema implementa um fluxo completo de recuperação de senha via e-mail, utilizando tokens criptograficamente seguros com tempo de expiração.

### 3.1 Fluxo de Recuperação

1. Usuário acessa `/recuperar-senha` e informa seu e-mail
2. Sistema consulta o banco **sem revelar se o e-mail existe** (prevenção de enumeração)
3. Token gerado com `secrets.token_urlsafe(32)` — 256 bits de entropia
4. Token armazenado no banco com expiração de **1 hora**
5. Link de redefinição enviado via Brevo API
6. Usuário acessa o link e redefine a senha
7. Token invalidado após uso (campos zerados no banco)

### 3.2 Segurança do Token

O módulo `secrets` do Python é utilizado para geração do token, garantindo entropia criptograficamente segura. O token possui **32 bytes (256 bits)** de tamanho, tornando ataques de força bruta computacionalmente inviáveis.

### 3.3 Tabela de Requisitos — Recuperação de Senha

| Nº | Requisito | Status |
|----|-----------|--------|
| 2.1 | Funcionalidade de recuperação implementada | ✅ Atendido |
| 2.2 | Token criptograficamente seguro (`secrets`) | ✅ Atendido |
| 2.3 | Token com tempo de expiração (1 hora) | ✅ Atendido |
| 2.4 | Token invalidado após uso | ✅ Atendido |
| 2.5 | Falha correta para token expirado | ✅ Atendido |
| 2.6 | Registro de solicitação em log | ⚠️ Parcial |
| 2.7 | Registro de sucesso/falha | ⚠️ Parcial |

---

## 4. Criptografia e Comunicação Segura

### 4.1 TLS/HTTPS

A comunicação entre cliente e servidor é protegida por TLS via HTTPS. Em ambiente de produção (Render), o HTTPS é provisionado automaticamente com certificado SSL/TLS válido. O **Flask-Talisman** adiciona o header `Strict-Transport-Security` (HSTS) que instrui os navegadores a sempre utilizarem HTTPS.

### 4.2 Headers de Segurança HTTP (Flask-Talisman)

| Header | Proteção |
|--------|----------|
| `Content-Security-Policy` | Restringe origens de scripts e recursos (XSS) |
| `X-Frame-Options: SAMEORIGIN` | Bloqueia clickjacking via iframe |
| `X-Content-Type-Options: nosniff` | Impede MIME sniffing |
| `Strict-Transport-Security` | Força uso de HTTPS (HSTS) |
| `Referrer-Policy` | Controla informações de referência |
| `Permissions-Policy` | Restringe APIs do navegador |

### 4.3 Proteção de Dados Sensíveis

Todas as credenciais e configurações sensíveis são armazenadas em **variáveis de ambiente** via arquivo `.env` (python-dotenv), nunca expostas no código-fonte ou repositório Git. O `.gitignore` garante que o arquivo `.env` não seja versionado.

### 4.4 Tabela de Requisitos — Criptografia

| Nº | Requisito | Status |
|----|-----------|--------|
| 3.1 | Comunicação protegida por TLS/HTTPS | ✅ Render + Talisman |
| 3.2 | Bloqueio de conexões não seguras | ✅ HSTS via Talisman |
| 3.3 | Evidência de tráfego cifrado | ✅ Print HTTPS incluso |
| 3.4 | Dados sensíveis criptografados em repouso | ✅ bcrypt nas senhas |
| 3.5 | Algoritmo criptográfico adequado | ✅ bcrypt (derivação de chave) |
| 3.6 | Chaves criptográficas protegidas | ✅ `.env` + `.gitignore` |
| 3.7 | Estratégia de criptografia documentada | ✅ Este documento |
| 3.8 | Justificativa técnica das escolhas | ✅ Este documento |

---

## 5. Conformidade com a LGPD

A Lei Geral de Proteção de Dados (Lei nº 13.709/2018) estabelece diretrizes para coleta, armazenamento e tratamento de dados pessoais. O sistema coleta dados mínimos necessários para seu funcionamento.

### 5.1 Dados Pessoais Coletados

| Dado | Finalidade | Base Legal |
|------|------------|------------|
| Nome de usuário | Identificação no sistema | Execução de contrato |
| E-mail | Recuperação de senha e 2FA | Execução de contrato |
| Senha (hash) | Autenticação segura | Execução de contrato |
| Perfil (Role) | Controle de acesso | Execução de contrato |

### 5.2 Minimização de Dados

O sistema coleta apenas os dados estritamente necessários para o funcionamento, seguindo o **princípio da minimização** previsto no Art. 6º, III da LGPD. Não são coletados dados como CPF, endereço, telefone ou quaisquer dados sensíveis desnecessários.

### 5.3 Direitos dos Titulares

O sistema prevê as seguintes funcionalidades para atendimento aos direitos dos titulares (Art. 18 da LGPD):

- **Acesso aos dados** — usuário pode visualizar seus dados na área logada
- **Retificação** — possibilidade de alteração de senha
- **Exclusão** — remoção da conta mediante solicitação

---

## 6. Auditoria e Logs

O sistema utiliza o sistema de logging nativo do Flask (`app.logger`) para registro de eventos relevantes de segurança.

### 6.1 Eventos Registrados

- Erros no envio de e-mail de recuperação de senha
- Erros no envio de código 2FA
- Exceções não tratadas nas rotas

### 6.2 Exemplo de Log

```
[2026-04-29 10:43:46] ERROR — Erro ao enviar e-mail de recuperação: (502, ...)
```

---

## 7. Identificação de Ameaças e Contramedidas

| Ameaça | Risco | Contramedida |
|--------|-------|--------------|
| Força bruta em senhas | Alto | bcrypt fator 12 + 2FA |
| Roubo de senha (DB leak) | Alto | bcrypt — hash irreversível |
| Phishing / CSRF | Médio | Talisman CSP + SameSite |
| XSS | Médio | CSP via Flask-Talisman |
| Clickjacking | Baixo | `X-Frame-Options: SAMEORIGIN` |
| Token de reset interceptado | Médio | HTTPS + expiração 1h |
| Enumeração de e-mails | Baixo | Resposta genérica no reset |
| Credenciais expostas no código | Alto | `.env` + `.gitignore` |

---

## 8. Resumo Científico

Este trabalho apresenta o desenvolvimento de um sistema de autenticação seguro para ambiente clínico psicológico, implementado em Python com o framework Flask. O objetivo principal foi construir uma aplicação que atenda aos requisitos de segurança contemporâneos, com ênfase na proteção de credenciais, comunicação segura e conformidade com a Lei Geral de Proteção de Dados (LGPD).

A metodologia adotada baseou-se nas diretrizes do **OWASP** (Open Web Application Security Project) e nas recomendações do **NIST** para gerenciamento de identidade e autenticação. Para o armazenamento seguro de senhas, foi utilizado o algoritmo bcrypt com fator de custo 12, que incorpora salt aleatório por usuário e resistência adaptável a ataques de força bruta, conforme recomendado pelo NIST SP 800-63B.

A autenticação de dois fatores foi implementada via código de verificação enviado por e-mail, adicionando uma camada adicional de proteção contra comprometimento de credenciais. A comunicação entre cliente e servidor é protegida por TLS/HTTPS em ambiente de produção, com headers de segurança HTTP configurados via Flask-Talisman, incluindo Content-Security-Policy, HSTS e proteções contra clickjacking.

Em relação à conformidade com a LGPD, o sistema adota o princípio da minimização de dados, coletando apenas informações estritamente necessárias para o funcionamento, com base legal fundamentada na execução contratual. As chaves criptográficas e credenciais de serviços externos são protegidas por variáveis de ambiente, eliminando a exposição de segredos no código-fonte.

Os resultados demonstram que é possível implementar um sistema de autenticação robusto com ferramentas open-source, alinhado às normas de segurança e à legislação brasileira de proteção de dados. Como trabalhos futuros, propõe-se a implementação de rate limiting para proteção contra força bruta, autenticação TOTP (RFC 6238) e sistema de auditoria de logs persistente.

**Palavras-chave:** Autenticação segura · bcrypt · Flask · LGPD · Dois fatores · TLS · OWASP
