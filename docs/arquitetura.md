# Arquitetura do Fluxo de Publicações

```text
[Coletor Scrapy] --(dados brutos)--> [Pipeline de Normalização] --(dados limpos)--> [Persistência / Banco de Dados]
          \
           \--(metadados e logs)--> [Monitoramento]

[Persistência / Banco de Dados] --(consultas)--> [API Service] --(respostas JSON)--> [Consumidores]
```

1. **Coletor Scrapy**: spiders coletam publicações nas fontes de interesse e enviam os dados para o pipeline de normalização.
2. **Pipeline de Normalização**: transforma os dados brutos em um formato padronizado, enriquecendo com metadados e verificações de qualidade.
3. **Persistência**: armazena os dados normalizados em um banco de dados otimizado para consultas rápidas.
4. **API Service**: expõe endpoints que consomem os dados persistidos e os disponibilizam para sistemas internos, parceiros ou dashboards.
