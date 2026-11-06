# Revisão solicitada pela Lacrei Saúde — 06/11/2026

## Alterações preparadas

1. `README.md` alinhado com o `compose.aws.yml` já versionado e o teste de restauração de produção realizado, sem declarar execução nova que não ocorreu.
2. Instruções de Docker, Poetry+PostgreSQL, variáveis `.env.aws` e exemplo de Caddy incluídos no README.
3. `aplicar_json.py` insere `JSONRenderer` no Django REST Framework **sem sobrescrever** outras configurações. `api/tests/test_json_responses.py` valida JSON, erros e a interface Swagger.
4. `.github/workflows/ci-cd.yml` faz deploy do `github.sha` aprovado, aborta quando a branch mudou e registra `DEPLOYED_SHA`, verificando saúde local e pública.
5. O workflow escreve no GitHub Actions Step Summary SHA e URL do run. O README explica como obter links diretos de cada pipeline e testes da **nova revisão**.
6. O README explica limites do rollback de código versus migrações/backup do banco.

## Importante: estado verificado e pendências

- Esta revisão foi construída a partir de um ZIP de código fornecido anteriormente e de cópias mais recentes de README/workflow presentes na conversa. **Não há acesso ao HEAD remoto do GitHub nesta sessão**. Compare os arquivos com seu repositório antes de copiar; não sobrescreva mudanças posteriores.
- Testes Django e execução real de CI/deploy não foram executados nesta sessão porque os serviços/dependências e credenciais do projeto não estão disponíveis. Há validações estáticas dos arquivos, mas não equivalem a pipeline verde.
- Após aplicar e fazer commit, as URLs dos runs precisam ser recolhidas do GitHub Actions. Não invente SHA, run ID, nem evidência de aprovação.
- Não mexe em S3, IAM, Asaas, dados reais, credenciais nem migrações de banco.

## Aplicação segura no seu clone local (Linux Mint)

**Execute na pasta do seu clone atual; não envie esta pasta inteira por cima do repositório.**

```bash
cd ~/caminho/para/lacrei-saude-desafio
# garanta que não existam alterações locais não commitadas antes de proceder
 git status --short
 git switch -c revisao-lacrei-novembro
# Extraia o ZIP numa pasta separada, por exemplo ~/Downloads/lacrei-revisao-06-11-2026
# Compare README e workflow com as versões atuais, depois copie apenas os arquivos desejados.
# Na raiz do clone, copie aplicar_json.py e execute: python3 aplicar_json.py
python3 -m compileall -q config api
poetry run python manage.py test
poetry run ruff check .
poetry run python manage.py makemigrations --check --dry-run
 git diff --check
```

Se os testes passarem, `git add` nos arquivos relevantes, faça commit e envie branch para PR. Ao integrar em `develop`, observe o pipeline staging. Depois de validar, integre em `main` e observe pipeline produção. **Publicação em produção não é feita automaticamente por este ZIP.**

Ao responder ao e-mail, anexe links dos runs de `develop` e `main` e indique o SHA do commit revisado; os SHAs serão diferentes se as branches receberem commits de merge distintos, e isso é normal.
