# Lacrei Saúde — Desafio Back-end

API REST de gerenciamento de **profissionais de saúde** e **consultas médicas**, criada com
Python, Django REST Framework, PostgreSQL, Docker, Poetry e GitHub Actions.

## 1. Funcionalidades

- CRUD completo de profissionais e consultas, com respostas JSON e paginação.
- Consulta de registros por ID e filtro `GET /api/consultas/?profissional_id=1`.
- Dados: profissionais (`nome_social`, `profissao`, `endereco`, `contato`);
  consultas (`data` ISO 8601 com fuso, `profissional` FK).
- Login via token, validação de dados, rejeição de HTML, SQL parametrizado pelo Django ORM.
- CORS restritivo, requisições limitadas por usuário, logs de acesso e erros.
- PostgreSQL, migrations, Swagger, testes com `APITestCase`.
- Pipeline GitHub Actions com lint, migration check, testes, build e gatilhos de deploy.

## 2. Pré-requisitos

- Docker + plugin `docker compose` instalados, ou Python 3.12 e Poetry 2.x.
- `git` para o repositório remoto.

### Execução com Docker (recomendado)

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
curl http://127.0.0.1:8000/health/
```

Resultado esperado: `{"status":"ok"}`.

As migrations são aplicadas automaticamente na inicialização do container web.
As tabelas ficam armazenadas no volume `postgres_data`.

Crie um usuário (senha individual e forte):

```bash
docker compose exec web python manage.py createsuperuser
```

### Login e utilização

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"SEU_USUARIO","password":"SUA_SENHA"}'
```

Copie o token retornado apenas para o seu terminal e **nunca commite em arquivos**.

```bash
export TOKEN="COLE_O_TOKEN_AQUI"

curl -X POST http://127.0.0.1:8000/api/profissionais/ \
  -H "Authorization: Token $TOKEN" -H 'Content-Type: application/json' \
  -d '{"nome_social":"Alex Oliveira","profissao":"Psicologia","endereco":"Rua Um, 10","contato":"alex@example.com"}'

curl -X POST http://127.0.0.1:8000/api/consultas/ \
  -H "Authorization: Token $TOKEN" -H 'Content-Type: application/json' \
  -d '{"data":"2026-11-10T14:00:00-03:00","profissional":1}'

curl -H "Authorization: Token $TOKEN" \
  'http://127.0.0.1:8000/api/consultas/?profissional_id=1'
```

Se você criar outros registros antes, substitua `1` pelo ID real do profissional.

## 3. Endpoints

| Método | Rota | Descrição |
|--|--|--|
| GET | `/health/` | Verifica app e banco (público) |
| POST | `/api/auth/token/` | Obtém token com usuário e senha |
| GET/POST | `/api/profissionais/` | Lista/cria profissional |
| GET/PUT/PATCH/DELETE | `/api/profissionais/{id}/` | Detalhe/atualiza/exclui profissional |
| GET/POST | `/api/consultas/` | Lista/cria consulta |
| GET/PUT/PATCH/DELETE | `/api/consultas/{id}/` | Detalhe/atualiza/exclui consulta |
| GET | `/api/consultas/?profissional_id={id}` | Filtra consultas por profissional |
| GET | `/api/schema/` | OpenAPI |
| GET | `/api/docs/` | Swagger UI |

Status HTTP padrão: `200` leitura/edição, `201` criação, `204` exclusão,
`400` validação, `401` sem autenticação, `404` recurso não encontrado,
`409` tentativa de excluir profissional com consultas e `429` limite de requisições.

**Regra de integridade:** profissional com consultas não pode ser excluído até
que essas consultas sejam removidas. Essa é uma decisão documentada de proteção de dados.

## 4. Executar testes

```bash
docker compose exec web python manage.py test
# ou, fora do Docker, depois de instalar dependências com Poetry:
# poetry run python manage.py test
# poetry run ruff check .
```

Os testes usam `APITestCase`, incluindo autenticação, CRUD, erro 400/404,
filtragem, tentativa de injeção SQL e integridade referencial.

## 5. Instalação sem Docker (alternativa para desenvolvimento)

```bash
python3.12 -m pip install --user poetry
poetry install --no-root
# crie .env com DEBUG=1 e DATABASE_URL=sqlite:///db.sqlite3 só para rodar local
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py runserver
```

A entrega/CI utiliza PostgreSQL; SQLite aqui é apenas alternativa de desenvolvimento.

## 6. Arquitetura e decisões

```text
Cliente/API Consumer
       |
       | HTTPS + Authorization: Token ...
       v
Django REST Framework -> Serializers -> ModelViewSet -> Django ORM
       |                                     |
  validação, auth,                           v
  CORS, throttling                      PostgreSQL
       |
   stdout logs
```

- Django 5.2 LTS para estabilidade e ampla compatibilidade.
- ViewSets permitem rotas CRUD padronizadas e reduzem código duplicado.
- Token simples atende ao requisito; para produção de longa duração,
  recomendar token com expiração/rotação (Knox ou JWT) e HTTPS obrigatório.
- `PROTECT` evita apagar histórico de consultas por exclusão acidental.
- ORM parametriza queries e mitiga injeção de SQL; entrada também é validada.
- CORS restringe origens do navegador **mas não substitui autenticação**.
- Logs omitem body, querystring e token; configure retenção com cuidado.
- DRF pagination: 20 resultados por página por padrão.
- Swagger adicionado como bônus de documentação, em `/api/docs/`.

## 7. CI/CD e deploy — staging e produção

O GitHub Actions (`.github/workflows/ci-cd.yml`) realiza:

1. `ruff check .` (lint)
2. `makemigrations --check --dry-run` (sincronismo do schema)
3. `manage.py test` (PostgreSQL real em container de serviço)
4. `docker build` (build do serviço)
5. Deploy via **Render Deploy Hook**, separado por ambiente e branch.

### Como criar os 2 ambientes na Render

1. Publique o repo no GitHub, usando `develop` e `main`.
2. Render > New > Postgres: crie um banco distinto para `staging` e outro para
   `production` (confirme custos/planos na tela antes de aprovar).
3. Render > New > Web Service > Connect repository > escolha **Docker**.
   Serviço `lacrei-staging`: branch `develop`, Auto Deploy **Off**.
   Serviço `lacrei-production`: branch `main`, Auto Deploy **Off**.
4. Em cada serviço, Configure Environment (não salve segredos no código):
   - `DEBUG=0`
   - `DJANGO_SECRET_KEY`: chave exclusiva e aleatória
   - `DATABASE_URL`: URL **do banco correto** de cada ambiente
   - `ALLOWED_HOSTS`: hostname atribuído àquele serviço
   - `CORS_ALLOWED_ORIGINS`: somente frontend(s) confiáveis, se houver
   - `CSRF_TRUSTED_ORIGINS`: origem HTTPS do admin se necessário
   - `DATABASE_SSL_REQUIRE`: de acordo com exigência do provedor do banco
5. Configure **Health Check Path** para `/health/`.
6. No Render > Service > Settings, copie o **Deploy Hook URL** do staging
   e separadamente do production.
7. GitHub > Settings > Environments: crie ambientes `staging` e `production`.
   Em cada um adicione o segredo de MESMO NOME `RENDER_DEPLOY_HOOK`, com
   a URL de deploy correspondente. Se disponível, exija aprovação manual
   para a produção. Nunca coloque hooks no README nem nos arquivos do repo.
8. Push para `develop` dispara staging; push para `main` dispara produção.
   **Confira logs do Render e GET /health/ após o deploy.**

A etapa do GitHub confirma o *disparo* do deploy, não que o serviço já ficou
saudável. Esse check final é obrigatório para a validação da entrega.

### Gerar uma chave forte

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(64))'
```

### Comandos Git para publicar

```bash
git init
git add .
git commit -m "feat: implementa API Lacrei Saúde"
git branch -M main
git remote add origin URL_DO_SEU_REPOSITORIO
git push -u origin main
git checkout -b develop
git push -u origin develop
```

**Importante:** gere `poetry.lock` com `poetry lock` (depois de instalar Poetry)
e inclua o arquivo no commit antes da entrega para garantir versões reproduzíveis.
Este pacote contém `pyproject.toml`, mas não um `poetry.lock` gerado: não foi
possível fazer a resolução online das dependências neste ambiente de preparo.

## 8. Rollback

Caso o novo deploy quebre em staging/produção:

1. Identificar o commit estável anterior no GitHub e o deploy na Render.
2. No Render > Deploys, selecionar **Rollback**/**Redeploy** do deploy estável
   (conforme controles disponíveis no serviço/plano).
3. Alternativa: reverter commit usando `git revert` e publicar na branch
   correspondente; o GitHub Actions disparará novo deploy.
4. Acompanhar `/health/`, logs da aplicação e endpoints autenticados.
5. **Banco:** migrations deste desafio são aditivas; reversão de schema é
   procedimento separado. Faça snapshot/backup antes de migrations destrutivas.
   Não execute `migrate api zero` em dados reais.

O rollback operacional depende das ferramentas e permissões disponíveis na
conta de hospedagem. Valide efetivamente um rollback em staging.

## 9. Erros encontrados, melhorias e limitações

- Sem pagamento real: proposta Asaas fica fora do escopo obrigatório.
- Não há dados reais de pacientes armazenados — usar apenas dados sintéticos
  na avaliação e nos logs.
- Token simples não expira por padrão; rotação, autorização por papéis,
  auditoria detalhada, backups e testes de carga são melhorias para produção.
- As configurações finais de domínio, secrets, URL de staging/produção,
  monitoramento e política de backup dependem da conta de deploy.
- Os testes e deploy precisam ser executados e validados antes do envio.

## 10. Checklist de entrega

- [ ] `docker compose up --build -d` sem erros
- [ ] `/health/` retorna 200
- [ ] API CRUD funcionando e filtro por ID validado
- [ ] `manage.py test` verde (testes em PostgreSQL)
- [ ] `ruff check .` verde
- [ ] Workflow GitHub Actions verde
- [ ] URL pública staging funcional
- [ ] URL pública produção funcional
- [ ] Rollback testado em staging
- [ ] README atualizado com links reais e decisões técnicas
- [ ] `poetry.lock` versionado, `.env` fora do Git

## 11. Extra opcional: integração Asaas

Desenho proposto, **não implementado**:

1. Um `Pagamento` referencia uma consulta e o identificador externo no Asaas.
2. Backend cria cobrança no Asaas via HTTP no servidor; credenciais apenas em secrets.
3. Webhook autenticado/validado atualiza o status de pagamento de modo
   **idempotente** (evento duplicado não gera duplicação).
4. Não armazenar cartão; conciliar divergências e documentar estado da cobrança.
5. Separar sandbox do Asaas em staging e conta real em produção.
