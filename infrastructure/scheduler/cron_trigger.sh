#!/usr/bin/env bash
# Dispara o coletor localmente via cron.
#
# Variáveis de ambiente esperadas:
#   SCRAPY_PROJECT_ROOT - diretório base do projeto.
#   RUN_ID              - identificador único da execução.
#   PROFILE_ID          - identificador do perfil a ser coletado.
#   JANELA_DIAS         - quantidade de dias retroativos considerados.
#
# Exemplos de uso no crontab (executa a cada 6 horas):
#   0 */6 * * * RUN_ID=$(uuidgen) PROFILE_ID=123 \ \
#       JANELA_DIAS=7 SCRAPY_PROJECT_ROOT=/opt/sentinela \ \
#       /opt/sentinela/infrastructure/scheduler/cron_trigger.sh >> /var/log/sentinela-cron.log 2>&1
set -euo pipefail

: "${SCRAPY_PROJECT_ROOT:?Defina SCRAPY_PROJECT_ROOT apontando para o diretório do projeto}" 
: "${RUN_ID:?Defina RUN_ID para correlacionar logs e métricas}" 
: "${PROFILE_ID:?Defina PROFILE_ID com o alvo da coleta}" 
: "${JANELA_DIAS:?Informe JANELA_DIAS para a janela temporal da coleta}" 

cd "$SCRAPY_PROJECT_ROOT"

exec scrapy crawl posts \
    -s RUN_ID="$RUN_ID" \
    -a profile_id="$PROFILE_ID" \
    -a janela_dias="$JANELA_DIAS"
