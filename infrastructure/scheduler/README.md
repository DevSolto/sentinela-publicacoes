# Agendamento de coletas

Este diretório contém artefatos prontos para orquestrar a execução do coletor Scrapy.
O parâmetro `janela_dias` controla quantos dias retroativos devem ser considerados
na busca de publicações e comentários.

- `cron_trigger.sh`: script pensado para uso com `cron`. Recebe as variáveis de
  ambiente `RUN_ID`, `PROFILE_ID` e `JANELA_DIAS`. O valor de `RUN_ID` é utilizado
  para correlação de logs/metricas ao longo de todo o pipeline. `JANELA_DIAS`
  é repassado para o spider como argumento `-a janela_dias=...`.
- `collector-cronjob.yaml`: modelo de `CronJob` do Kubernetes. Substitua
  `{{ profile_id }}` e `{{ janela_dias }}` de acordo com a necessidade. O campo
  `RUN_ID` é preenchido automaticamente com o UID da execução do job.

Ao ajustar o agendamento, lembre-se de dimensionar a janela temporal (`janela_dias`)
para evitar sobreposição desnecessária de coletas e reduzir pressão na origem dos
conteúdos.
