# Sentinela Pública - Scraper Service

Microserviço construído com [NestJS](https://nestjs.com/) responsável por coletar publicações de perfis públicos do Instagram e preparado para ser estendido para outras redes sociais.

## Requisitos

- Node.js 20+
- npm 10+

## Configuração

O serviço utiliza variáveis de ambiente para autenticação e ajustes da API do Instagram:

| Variável | Descrição |
| --- | --- |
| `INSTAGRAM_SESSION_ID` | (Opcional) Session ID de uma conta com acesso ao perfil alvo. Necessário para contornar limitações da API pública. |
| `INSTAGRAM_USER_AGENT` | (Opcional) User-Agent utilizado nas requisições. Um valor padrão compatível com navegadores modernos é aplicado automaticamente. |
| `INSTAGRAM_HEADERS` | (Opcional) Objeto JSON com cabeçalhos adicionais que serão enviados nas requisições ao Instagram. |
| `INSTAGRAM_BASE_URL` | (Opcional) URL base da API web do Instagram. Padrão: `https://www.instagram.com/api/v1/users/web_profile_info/`. |
| `INSTAGRAM_DEFAULT_LIMIT` | (Opcional) Quantidade padrão de publicações retornadas ao consultar um perfil. |

Crie um arquivo `.env` na raiz do projeto para definir essas variáveis quando necessário.

## Instalação

```bash
npm install
```

## Execução

```bash
# desenvolvimento
npm run start:dev

# produção
npm run build
npm run start:prod
```

A API é exposta no endereço `http://localhost:3000/api`.

## Rotas principais

- `GET /api/health` — verificação simples de disponibilidade.
- `GET /api/scraper/instagram/:username/posts?limit=10` — retorna as últimas publicações públicas do usuário informado.

## Testes

```bash
npm run test          # testes unitários
npm run test:e2e      # testes end-to-end
npm run test:cov      # cobertura de testes
```

## Próximos passos

- Adicionar estratégias de scraping para outras redes sociais.
- Implementar filas e agendamentos para coletas periódicas.
- Persistir as publicações em um banco de dados para consultas históricas.
