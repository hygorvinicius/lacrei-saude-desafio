# Revisão do desafio Lacrei Saúde — evidências confirmadas em 06/11/2026

Este guia registra **resultados confirmados diretamente nos pipelines** para os seis ajustes solicitados pela equipe. Não inclui credenciais, tokens ou dados reais de pacientes.

## 1. README e compose AWS
O `compose.aws.yml` está versionado e define os serviços Django/Gunicorn e PostgreSQL sem expor a porta 5432. Os arquivos `.env` e `.env.aws` não devem ser versionados. O README foi alinhado à configuração atual.

## 2. Execução e AWS
O README documenta inicialização com Docker Compose, alternativa local com Poetry e PostgreSQL, exemplo de `.env.aws` com valores fictícios, Caddy e verificação de saúde pública. A preparação automática de uma nova instância não foi exercitada nesta revisão.

## 3. JSON e Swagger
`REST_FRAMEWORK.DEFAULT_RENDERER_CLASSES` contém apenas `JSONRenderer` para a API; a rota `/api/docs/` continua disponível em HTML. O arquivo `api/tests/test_json_responses.py` contém oito testes adicionais para JSON, erros, autenticação, saúde e Swagger. Os 23 testes do projeto passaram na execução #17.

## 4. Deploy rastreável
O workflow `.github/workflows/ci-cd.yml` exige checkout exato de `GITHUB_SHA` no servidor, compara com o HEAD remoto da branch, registra `DEPLOYED_SHA` e verifica `/health/` localmente e por HTTPS, nos dois ambientes. Os logs dos jobs de deploy confirmaram esses SHAs na revisão.

## 5. Evidências diretas

| Ambiente | Commit implantado | Pipeline | Job de qualidade |
|---|---|---|---|
| Staging | `d12e6725e285117cfbf6e14a160f03260d209368` | [Run #15](https://github.com/hygorvinicius/lacrei-saude-desafio/actions/runs/42253316511) | [Testes e lint](https://github.com/hygorvinicius/lacrei-saude-desafio/actions/runs/42253316511/job/128013818318) |
| Produção | `cf5ad971ef92aa0754450bc22e53a009384e5e01` | [Run #17](https://github.com/hygorvinicius/lacrei-saude-desafio/actions/runs/42253783256) | [Testes e lint](https://github.com/hygorvinicius/lacrei-saude-desafio/actions/runs/42253783256/job/128015409584) |

[PR #1](https://github.com/hygorvinicius/lacrei-saude-desafio/pull/1) e [PR #2](https://github.com/hygorvinicius/lacrei-saude-desafio/pull/2) estão integrados.

- [Staging — /health/](https://18-227-202-242.sslip.io/health/)
- [Produção — /health/](https://3-133-248-90.sslip.io/health/)
- [Staging — Swagger](https://18-227-202-242.sslip.io/api/docs/)
- [Produção — Swagger](https://3-133-248-90.sslip.io/api/docs/)

## 6. Funcionamento e rollback
Houve teste de rollback de **código** no staging em 05/11/2026, com retorno ao commit anterior e posterior restauração da versão em uso; o endpoint de saúde respondeu. O README documenta os passos e seus limites.

**O rollback de código não desfaz migrações nem restaura automaticamente dados PostgreSQL.** Alterações de esquema incompatíveis exigem planejamento, backup, testes e eventual recuperação separada. O dump de produção foi restaurado em um contêiner PostgreSQL isolado, com 13 tabelas; isso não comprova restauração completa de todo o sistema em caso de desastre.

## Limites desta verificação
Aprovação dos pipelines e resposta de `/health/` não equivalem a auditoria independente de segurança, LGPD, observabilidade, disponibilidade contínua ou testes de desempenho. As evidências acima se referem às execuções de 06/11/2026. O extra Asaas permanece opcional e não implementado.
