# Sentinela Publicações Monorepo

Este monorepo reúne todos os serviços do ecossistema Sentinela, responsáveis por coletar, tratar e disponibilizar publicações monitoradas. A estrutura foi organizada para facilitar o desenvolvimento independente de cada serviço enquanto mantém um fluxo de entrega integrado.

## Estrutura dos diretórios

- `scrapy_service/`: serviço de coleta que utiliza spiders Scrapy para buscar publicações nas fontes monitoradas.
- `api_service/`: serviço de API responsável por disponibilizar os dados normalizados e persistidos para consumo interno e externo.
- `infrastructure/`: scripts e definições de infraestrutura como código, além de ferramentas de observabilidade e automação de deploy.
- `docs/`: documentação técnica e operacional do monorepo.

## Requisitos gerais

Cada serviço possui suas próprias dependências para garantir isolamento. Recomenda-se utilizar ambientes virtuais separados (por exemplo, `python -m venv .venv && source .venv/bin/activate`).

## Como executar os serviços

### Scrapy Service
1. Acesse o diretório do serviço:
   ```bash
   cd scrapy_service
   ```
2. Crie e ative um ambiente virtual, se necessário.
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute a spider desejada:
   ```bash
   scrapy crawl <nome_da_spider>
   ```

#### Execução manual e gerenciamento de perfis

Para executar a coleta manualmente e manter uma lista de perfis monitorados,
utilize o utilitário `scrapy_service.cli`:

- Adicionar ou atualizar um perfil no arquivo `profiles.json` (criado
  automaticamente caso não exista):
  ```bash
  python -m scrapy_service.cli add-profile sentinela \
      "https://rede.social/@sentinela" \
      --display-name "Sentinela" \
      --scroll-limit 5
  ```
- Executar a spider de perfis apenas para o identificador informado:
  ```bash
  python -m scrapy_service.cli run-profiles --profile-id sentinela --run-id $(uuidgen)
  ```

O comando `run-profiles` aceita múltiplos `--profile-id` e também permite
sobrescrever parâmetros como `--scroll-limit` e `--scroll-delay` somente para a
execução atual. Para aplicar configurações extras do Scrapy utilize `--setting
CHAVE=valor` (pode ser informado várias vezes).

### API Service
1. Acesse o diretório do serviço:
   ```bash
   cd api_service
   ```
2. Crie e ative um ambiente virtual, se necessário.
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Inicie o servidor de desenvolvimento:
   ```bash
   uvicorn app.main:app --reload
   ```

### Infrastructure
1. Acesse o diretório do serviço:
   ```bash
   cd infrastructure
   ```
2. Crie e ative um ambiente virtual, se necessário.
3. Instale as dependências para scripts auxiliares:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute os scripts de automação disponíveis (por exemplo, provisionamento via Terraform ou ferramentas CLI) conforme descrito na documentação específica do diretório.

## Documentação adicional

Consulte `docs/arquitetura.md` para entender o fluxo completo de dados do coletor até a exposição via API.
