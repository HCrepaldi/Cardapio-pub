# 🗺️ ROADMAP — Migração para Oracle Cloud (Always Free)

Documento de planejamento da migração da infraestrutura do site do **No Black Tie Pub**
para a **Oracle Cloud Infrastructure (OCI) — Always Free Tier**.

> **Meta:** concluir o projeto completo até **fevereiro/2026**, em ritmo tranquilo
> (conciliando com a reta final da faculdade).

---

## 🎯 Por que migrar?

**Situação atual:**
- **Site:** hospedado no Render (plano gratuito — "dorme" após inatividade, demora a acordar).
- **Banco:** PostgreSQL no Neon (plano gratuito — limite de **100 compute-hours/mês**).

**Problema que motivou a migração:**
Em outubro/2026, o banco Neon foi suspenso por estourar as 100h — causado por um
**ping 24/7** (UptimeRobot) que mantinha o banco sempre acordado. Os dados ficaram
seguros, mas o acesso foi bloqueado até o reset do ciclo.

**Solução escolhida:**
Migrar para uma **VM Always Free da Oracle** (ARM Ampere, São Paulo), que fica
**sempre ligada, sem limite de horas** — hospedando tanto o **banco** quanto o **site**.

**Ganhos esperados:**
- ✅ Sem limite de compute-hours (fim do problema do Neon).
- ✅ Sem "cochilo" do Render (site sempre no ar, resposta instantânea).
- ✅ Sem necessidade de ping/UptimeRobot.
- ✅ Banco e site no mesmo servidor (comunicação local, rápida).
- ✅ Tudo gratuito e permanente.

**Trade-off assumido (consciente):**
Numa VM, a manutenção é responsabilidade nossa (atualizações, backups, manter os
serviços no ar). É mais trabalho que um serviço gerenciado — mas é também um
**grande aprendizado** de administração de servidor Linux.

---

## 🧱 Estratégia: 4 fases independentes

Princípio: **cada fase deixa o site funcionando no final.** Dá para pausar entre
fases sem quebrar nada. O Neon/Render só saem de cena quando o substituto estiver
testado e funcionando.

### 🥇 Fase 1 — Banco de dados na VM Oracle
**Objetivo:** PostgreSQL rodando na VM, com os dados migrados do Neon.

- [ ] Criar a VM (Ubuntu, shape **Ampere ARM** — Always Free)
- [ ] Guardar a chave SSH com segurança
- [ ] Configurar rede/firewall (abrir porta 5432 do PostgreSQL com critério)
- [ ] Instalar o PostgreSQL na VM
- [ ] Criar banco, usuário e senha; habilitar conexão externa
- [ ] Montar a nova `DATABASE_URL`
- [ ] Migrar os dados do Neon (cardápio, mesas, shows, reservas)
- [ ] Trocar a `DATABASE_URL` no Render e testar

**Resultado:** site continua no Render, mas usando o banco da Oracle. Neon aposentado.
**Aprende:** VM, SSH, firewall, instalação/configuração de PostgreSQL.

---

### 🥈 Fase 2 — Subir o site (FastAPI) na VM
**Objetivo:** o app FastAPI rodando na VM, ao lado do banco.

- [ ] Instalar Python e dependências na VM
- [ ] Rodar o app com Uvicorn
- [ ] Configurar um serviço **systemd** (reinicia sozinho se cair / ao reiniciar a VM)
- [ ] Testar o acesso pelo IP da VM

**Resultado:** o site roda na VM (via IP); o domínio ainda aponta para o Render.
**Aprende:** deploy manual, ambiente Python em servidor, systemd.

---

### 🥉 Fase 3 — Nginx + HTTPS + domínio
**Objetivo:** servir o site com segurança, no domínio oficial.

- [ ] Instalar e configurar o **Nginx** (reverse proxy na frente do Uvicorn)
- [ ] Emitir certificado **SSL/HTTPS** (Let's Encrypt / certbot)
- [ ] Reapontar o DNS do domínio (registro.br) para o IP da VM
- [ ] Validar `https://noblacktiepub.com.br` servido pela Oracle

**Resultado:** domínio rodando da Oracle, com HTTPS. **Render pode ser desligado.**
**Aprende:** Nginx (reverse proxy), SSL/certificados, DNS.

---

### 🏅 Fase 4 — Robustez e manutenção
**Objetivo:** deixar tudo sustentável e seguro para o longo prazo.

- [ ] **Backup automático** do banco (agendado) — prioridade!
- [ ] Definir fluxo de **deploy** (como atualizar o site ao mexer no código)
- [ ] Ajustes de segurança (firewall, atualizações do sistema, senhas em variáveis)
- [ ] Documentar o processo (um "manual" do servidor)

**Resultado:** projeto completo, documentado e sustentável.
**Aprende:** backups, automação, boas práticas de administração.

---

## 🗓️ Sugestão de ritmo (flexível)

| Período | Fase |
|---|---|
| Nov–Dez/2026 | Fase 1 — Banco na VM |
| Dez/2026–Jan/2027 | Fase 2 — Site na VM |
| Jan/2027 | Fase 3 — Nginx/SSL/domínio |
| Fev/2027 | Fase 4 — Backup e finalização |

> As datas são só um guia — ajustar conforme a faculdade permitir.

---

## 📌 Notas e lembretes

- **Regra de ouro:** não desativar Neon/Render até o substituto estar testado e no ar.
- **Conta Oracle:** ativa e confirmada, região **Brazil East (São Paulo)**.
- **Atenção ao shape da VM:** escolher **Ampere (ARM)** para ser Always Free
  (em 2026 o Always Free dá ~2 OCPU / 12 GB RAM em ARM — mais que suficiente).
- **Segurança:** manter `DATABASE_URL` e `SENHA_ADMIN` como variáveis de ambiente
  (nunca no código). Trocar a senha do admin que vazou no histórico público do Git.
- **Backup:** a Fase 4 resolve de vez o risco de perder reservas — priorizar o backup
  automático assim que o banco estiver na VM.

---

*Documento vivo — atualizar os checkboxes conforme cada fase for concluída.*
