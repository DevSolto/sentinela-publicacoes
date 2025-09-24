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
