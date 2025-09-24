# Operação do coletor Sentinela

## Estratégia de backoff e jitter

O coletor utiliza um middleware de retries com backoff exponencial. Os parâmetros
podem ser ajustados via variáveis de ambiente:

- `SCRAPY_RETRY_TIMES`: quantidade máxima de tentativas (padrão `5`).
- `SCRAPY_RETRY_BACKOFF_BASE`: atraso inicial em segundos (padrão `1`).
- `SCRAPY_RETRY_BACKOFF_MAX`: atraso máximo aplicado ao agendamento das novas
  tentativas (padrão `60`).

Cada tentativa falha aumenta o delay segundo `delay = min(base * 2^(tentativas-1), max)`.
Recomenda-se aplicar jitter (ex.: `random.uniform(-0.2, 0.2) * delay`) antes de
reagendar requisições para evitar sincronia entre múltiplas execuções. Esse jitter
pode ser implementado ajustando `download_delay` nos metadados da requisição no
middleware `ExponentialBackoffRetryMiddleware`.

## Limites de concorrência

Os limites globais (`SCRAPY_CONCURRENT_REQUESTS`) e por domínio
(`SCRAPY_CONCURRENT_PER_DOMAIN`) controlam a quantidade de requisições simultâneas.
Ajuste-os conforme a capacidade da origem monitorada e a largura de banda
(distribuição: inicie com `8`/`4` e aumente gradualmente monitorando erros HTTP 429).

Para evitar saturar proxies ou a própria API de origem, combine esses parâmetros com
`DOWNLOAD_DELAY` (padrão `0`) e o campo `pagination_delay` dos spiders Playwright.

## Execução manual da coleta

Para disparar coletas sob demanda sem aguardar o agendamento padrão, utilize o
comando de utilidades empacotado com o serviço Scrapy:

```bash
cd scrapy_service
python -m scrapy_service.cli run-profiles --profile-id <identificador>
```

Antes disso, cadastre o perfil (caso ainda não exista no arquivo
`profiles.json`) com:

```bash
python -m scrapy_service.cli add-profile <identificador> "https://exemplo.com/perfil"
```

Ambos os comandos aceitam a flag `--profiles-file` para apontar um caminho
alternativo e podem ser versionados em repositórios de configuração para
garantir rastreabilidade das alterações.

## Rotação de proxies

A rotação é feita pelo middleware `ProxyRotationMiddleware`, que escolhe proxies a
partir da lista `SCRAPY_PROXIES` (CSV). Recomenda-se manter um pool atualizado e
executar rotação de credenciais/proxies semanalmente para evitar bloqueios. Em
ambientes Kubernetes, armazene os proxies em Secrets e atualize-os com rollout
controlado; em ambientes bare-metal, utilize arquivos de configuração versionados e
proceda com `ansible`/`scp` para distribuição segura.

1. Atualize a fonte de proxies (Secret ou arquivo).
2. Reinicie gradualmente os workers (jobs Cron ou pods) para aplicar a nova lista.
3. Monitore métricas de falhas (`scrapy_run_failures_total`) e códigos de status para
   validar a eficácia da rotação.
