# Lacrei Saúde — Desafio Técnico Back-end

API REST para cadastro de profissionais de saúde e gerenciamento de consultas, desenvolvida como desafio técnico de voluntariado da Lacrei Saúde.

**Repositório:** https://github.com/hygorvinicius/lacrei-saude-desafio

## Ambientes publicados

| Ambiente | Branch | Hospedagem | Documentação | Saúde |
|---|---|---|---|---|
| **Produção** | `main` | AWS Lightsail (`Ubuntu-1`) | [Swagger — produção](https://3-133-248-90.sslip.io/api/docs/) | [Health — produção](https://3-133-248-90.sslip.io/health/) |
| **Staging** | `develop` | AWS Lightsail (`Ubuntu-2`) | [Swagger — staging](https://18-227-202-242.sslip.io/api/docs/) | [Health — staging](https://18-227-202-242.sslip.io/health/) |

Os dois ambientes executam **Django + PostgreSQL em contêineres separados**, têm bases de dados independentes e recebem tráfego HTTPS por meio do **Caddy**. Endereços baseados em `sslip.io` são adequados para demonstração; os IPs devem permanecer associados às instâncias (idealmente como IPs estáticos) enquanto esses links forem usados.

**Situação verificada em 5 de novembro de 2026:** pipelines de produção e staging concluíram com sucesso; o commit de produção `6520934` e o commit de staging `97735b4` foram confirmados nos respectivos servidores. O endpoint `/health/` respondeu `200 OK` nos testes apresentados. Os endereços e commits representam o estado dessa validação, não garantia de disponibilidade futura.

## 1. Funcionalidades

- CRUD de profissionais de saúde (`nome_social`, `profissao`, `endereco`, `contato`).
- CRUD de consultas (`data` com fuso horário e `profissional` como chave estrangeira).
- Listagem paginada, busca por ID e filtro de consultas pelo ID do profissional.
- Autenticação por token (`Authorization: Token ...`).
- Validação de entradas, proteção contra exclusão indevida de profissional vinculado a consultas, uso do ORM do Django e configuração de CORS.
- Logs de acesso/erro, limitação de requisições e documentação OpenAPI/Swagger, conforme a implementação e a configuração do projeto.
- Testes automatizados com `APITestCase` e pipeline GitHub Actions.

### Rotas principais

| Método | Endpoint | Uso |
|---|---|---|
| GET | `/health/` | Verificação de saúde HTTP da API |
| POST | `/api/auth/token/` | Obter token com usuário e senha |
| GET, POST | `/api/profissionais/` | Listar ou criar profissionais |
| GET, PUT, PATCH, DELETE | `/api/profissionais/{id}/` | Consultar, editar ou excluir profissional |
| GET, POST | `/api/consultas/` | Listar ou criar consultas |
| GET, PUT, PATCH, DELETE | `/api/consultas/{id}/` | Consultar, editar ou excluir consulta |
| GET | `/api/consultas/?profissional_id={id}` | Filtrar consultas por profissional |
| GET | `/api/schema/` | Esquema OpenAPI |
| GET | `/api/docs/` | Interface Swagger |

Respostas usuais: `200` para leitura/edição, `201` para criação, `204` para exclusão, `400` para validação inválida, `401` para acesso sem credenciais, `404` para recurso inexistente, `409` para exclusão proibida por vínculo e `429` para requisições acima do limite configurado. O retorno exato depende da operação.

**Regra de negócio:** um profissional com consultas associadas não pode ser excluído enquanto os vínculos existirem; a proteção evita perda acidental de histórico.

## 2. Tecnologias e arquitetura

- Python 3.12, Django, Django REST Framework e Poetry.
- PostgreSQL 16 e Django ORM.
- Docker Engine e Docker Compose.
- Git e GitHub Actions (lint, checagem de migrações, testes, build e deploy).
- AWS Lightsail com Ubuntu, Caddy e HTTPS.
- Swagger/OpenAPI para exploração da API.

```text
                      Cliente HTTP / Swagger
                               |
                             HTTPS
                               |
                       Caddy (80 / 443)
                               |
                    127.0.0.1:8000 (host)
                               |
                     Django REST Framework
                   serializers / views / auth
                               |
                           Django ORM
                               |
                       PostgreSQL (Docker)

  AWS Lightsail — produção                AWS Lightsail — staging
  main / banco próprio                     develop / banco próprio
  Secrets e volumes próprios               Secrets e volumes próprios
```

**Decisões técnicas:** o ORM utiliza consultas parametrizadas, os serializers concentram validações e os ViewSets padronizam operações CRUD. O PostgreSQL não precisa ser exposto na internet; o Django acessa o banco pela rede Docker. CORS limita o uso pelo navegador, mas **não substitui autenticação/autorização**. O token simples é adequado ao escopo do exercício, mas não tem expiração automática e exige controles adicionais em operação prolongada.

## 3. Executar localmente com Docker

### Pré-requisitos

Git, Docker Engine e o plugin `docker compose` instalados. Os comandos abaixo são executados na raiz do repositório.

```bash
git clone https://github.com/hygorvinicius/lacrei-saude-desafio.git
cd lacrei-saude-desafio
cp .env.example .env
# Configure uma senha de banco e uma DJANGO_SECRET_KEY próprias para desenvolvimento.
docker compose up --build -d
docker compose ps
curl -i http://127.0.0.1:8000/health/
```

Resposta de aplicação esperada:

```json
{"status":"ok"}
```

O entrypoint do serviço web aplica as migrações antes de iniciar a API, conforme configuração do projeto. Não use credenciais de produção no desenvolvimento. Não publique `.env` ou `.env.aws` no Git.

Criar um administrador local, quando necessário:

```bash
docker compose exec web python manage.py createsuperuser
```

### Autenticação e exemplos de requisições

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"SEU_USUARIO","password":"SUA_SENHA"}'
```

Use o token retornado somente em ambiente seguro. Evite colá-lo em prints, tickets, commits ou logs.

```bash
export TOKEN="SEU_TOKEN_AQUI"

curl -X POST http://127.0.0.1:8000/api/profissionais/ \
  -H "Authorization: Token $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"nome_social":"Alex Oliveira","profissao":"Psicologia","endereco":"Rua Um, 10","contato":"alex@example.com"}'

curl -X POST http://127.0.0.1:8000/api/consultas/ \
  -H "Authorization: Token $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"data":"2026-11-10T14:00:00-03:00","profissional":1}'

curl -H "Authorization: Token $TOKEN" \
  'http://127.0.0.1:8000/api/consultas/?profissional_id=1'
```

Substitua `1` pelo ID efetivamente retornado ao cadastrar um profissional. Use dados fictícios nos exemplos e nos testes.

## 4. Executar testes e verificações

```bash
docker compose exec web python manage.py test
docker compose exec web python manage.py check
```

O pipeline também executa, com Poetry e PostgreSQL no runner:

```bash
poetry run ruff check .
poetry run python manage.py makemigrations --check --dry-run
poetry run python manage.py test
poetry run python manage.py check
```

Nos testes registrados durante o desenvolvimento, **15 testes passaram**. Eles contemplaram autenticação, operações de profissionais e consultas, filtragem, validação de dados e cenários de erro, conforme as suítes do repositório. As execuções posteriores de GitHub Actions para as duas branches também foram aprovadas.

## 5. Implantação na AWS Lightsail

Cada ambiente dispõe de sua própria instância Ubuntu, PostgreSQL e arquivo de configuração privado. No servidor, o projeto fica em `~/lacrei-saude-desafio` e utiliza:

- `.env.aws`: configurações e credenciais exclusivas do servidor (**não versionar**).
- `compose.aws.yml`: composição de serviços usada no Lightsail.
- `Dockerfile` e `docker/entrypoint.sh`: build e inicialização do Django.
- Caddy, com proxy reverso para `127.0.0.1:8000` e TLS automático.

Exemplo de gerenciamento **dentro de cada servidor**, já configurado:

```bash
cd ~/lacrei-saude-desafio
sudo docker compose --env-file .env.aws -f compose.aws.yml ps
sudo docker compose --env-file .env.aws -f compose.aws.yml logs web --tail=50
```

O serviço `web` publica apenas `127.0.0.1:8000:8000` no host. A porta `5432` do PostgreSQL não deve ser publicada no firewall do Lightsail. As portas `80/443` atendem o HTTPS, e a porta `22` deve ter acesso administrativo restrito sempre que viável.

**Pendência de reprodutibilidade:** o arquivo `compose.aws.yml` foi montado diretamente nos servidores e apareceu como **não rastreado** no staging (`git status --short`). Para que terceiros possam reconstruir o ambiente AWS do zero apenas com o repositório, é necessário adicionar uma versão **sem segredos** desse arquivo (ou um template) ao Git, juntamente com as instruções de provisionamento do Caddy. Isso ainda não foi validado como instalação do zero em uma terceira máquina.

### Variáveis de ambiente principais

| Variável | Finalidade |
|---|---|
| `DEBUG` | `0` na AWS |
| `DJANGO_SECRET_KEY` | Chave aleatória exclusiva por ambiente |
| `DATABASE_URL` | Conexão com PostgreSQL do ambiente correspondente |
| `DB_PASSWORD` | Senha do banco usada pelo Compose de servidor |
| `ALLOWED_HOSTS` | Hosts autorizados do Django |
| `CSRF_TRUSTED_ORIGINS` | Origem HTTPS permitida para CSRF |
| `CORS_ALLOWED_ORIGINS` | Origens confiáveis, quando existir frontend |
| `DATABASE_SSL_REQUIRE` | Conforme topologia/configuração da conexão ao banco |

Não reutilize senhas de produção em staging nem coloque valores reais dessas variáveis em issues, README ou GitHub.

## 6. CI/CD — GitHub Actions

Workflow: [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml). Visão das [execuções do GitHub Actions](https://github.com/hygorvinicius/lacrei-saude-desafio/actions).

1. **Qualidade:** lint (`ruff`), checagem de migrações, testes automatizados em PostgreSQL e `manage.py check`.
2. **Build:** construção da imagem Docker.
3. **Deploy staging:** push em `develop` → GitHub Actions → SSH para `Ubuntu-2` → atualização do código e `docker compose up -d --build` → verificação de `/health/`.
4. **Deploy produção:** push em `main` → mesmo processo na instância `Ubuntu-1`, usando o ambiente `production`.

O GitHub utiliza os ambientes `staging` e `production`, cada um com seus próprios segredos:

- `LIGHTSAIL_HOST`
- `LIGHTSAIL_SSH_KEY`
- `LIGHTSAIL_KNOWN_HOSTS`

O par de chaves SSH é separado por ambiente, e a identidade SSH do host deve ser verificada antes de registrar `KNOWN_HOSTS`. As chaves privadas ficam nos segredos do GitHub, não no repositório.

**Incidente resolvido:** o primeiro deploy de staging falhou com `curl: (56) Recv failure: Connection reset by peer` porque o teste chegou durante a inicialização do Django. A verificação foi ajustada para tolerar erros transitórios e repetir as tentativas (`--retry-all-errors`, intervalo entre tentativas). A execução seguinte concluiu com sucesso.

**Validações observadas:** produção — commit `6520934`; staging — commit `97735b4` (execução #5, 5/11/2026). Um job verde comprova a execução da pipeline, e o teste externo de `/health/` acrescenta a confirmação de que o serviço respondeu; nenhum desses testes isolados equivale a uma auditoria completa de segurança ou desempenho.

## 7. Rollback operacional

O rollback de **código** foi testado no `Ubuntu-2` em 5/11/2026:

1. A branch `develop` estava no commit `97735b4`.
2. O servidor foi colocado temporariamente no commit anterior `6520934` (`git switch --detach 6520934`).
3. A imagem Django foi reconstruída com `sudo docker compose --env-file .env.aws -f compose.aws.yml up -d --build`.
4. O `/health/` voltou a responder `{"status":"ok"}` (após uma nova tentativa enquanto o serviço iniciava).
5. A branch `develop` e o commit `97735b4` foram restaurados; contêineres saudáveis e `/health/` respondendo novamente.

### Procedimento manual de emergência (ambiente já preparado)

Faça primeiro snapshot/backup do banco, identifique um commit estável compatível com as migrações e comunique a intervenção. No servidor afetado:

```bash
cd ~/lacrei-saude-desafio
git status --short
git log -5 --oneline
# Escolha o commit estável após confirmar compatibilidade:
git switch --detach COMMIT_ESTAVEL
sudo docker compose --env-file .env.aws -f compose.aws.yml up -d --build
curl --fail --show-error --retry-all-errors --retry 24 --retry-delay 5 \
  --max-time 8 -H 'X-Forwarded-Proto: https' \
  http://127.0.0.1:8000/health/
```

Para restaurar a branch após o incidente (exemplo **apenas staging**):

```bash
git switch develop
git pull --ff-only origin develop
sudo docker compose --env-file .env.aws -f compose.aws.yml up -d --build
```

**Limites:** o teste executado demonstrou retorno de *commit* e reconstrução de contêiner; os dois commits usados diferiam principalmente no workflow CI/CD. Não demonstrou migração reversa de banco, recuperação de indisponibilidade complexa nem rollback automático. Um push posterior pode sobrescrever o rollback manual. Nunca use `docker compose down -v` para esse procedimento: ele pode remover volumes com dados.

## 8. Backups e recuperação

Foi criado no servidor de staging um dump SQL do PostgreSQL, salvo em `~/lacrei-staging-backup.sql`, com cerca de 28 KB. Confirmou-se que o arquivo existe e não está vazio, **mas não foi executado teste de restauração**.

Exemplo de geração de um novo backup no servidor:

```bash
umask 077
cd ~/lacrei-saude-desafio
sudo docker compose --env-file .env.aws -f compose.aws.yml exec -T db \
  pg_dump -U lacrei -d lacrei > "$HOME/lacrei-staging-backup.sql"
test -s "$HOME/lacrei-staging-backup.sql" && echo 'Arquivo de backup nao vazio'
```

Próximos controles recomendados: testar restauração em banco descartável, definir retenção e periodicidade, copiar backups criptografados para fora da instância (por exemplo, um armazenamento privado com acesso mínimo) e documentar responsáveis e tempos de recuperação. Não incluir dumps no Git.

## 9. Problemas encontrados e melhorias propostas

| Problema/decisão | Tratamento ou pendência |
|---|---|
| Autenticação SSH recusada inicialmente | Chave pública adicionada a `authorized_keys`; conexões SSH autenticadas foram validadas |
| Pipeline de produção inicialmente dependente do Render | Substituído por deploy SSH no AWS Lightsail |
| Staging retornava `curl (56)` imediatamente após deploy | Adicionadas tentativas no Health Check; pipeline passou |
| Necessidade de manter dados entre reconstruções | Volume persistente do PostgreSQL, sem `down -v` |
| Compose AWS criado diretamente no servidor | **Pendente** versionar template seguro e reproduzível |
| Arquivo de backup de staging | Criado; **pendente** testar restauração e cópia externa |
| Tokens do DRF | Modelo simples sem expiração nativa; planejar expiração/rotação, escopos e revogação |
| Monitoramento e proteção de produção | Revisar alertas, logs, firewall, backups, rate limits e políticas de acesso |
| Integração Asaas | **Proposta não implementada** (item opcional) |

Não usar dados reais de pacientes ou credenciais reais nos testes e nas demonstrações. Antes de um uso prolongado em produção, revisar permissões, configurações do Django (`check --deploy`), política de dados e condições de manutenção dos servidores.

## 10. Checklist de entrega

- [x] CRUD e filtro de consultas implementados e testados no desenvolvimento.
- [x] Testes automatizados e verificações de qualidade aprovados nos pipelines observados.
- [x] Docker + PostgreSQL executados nos dois servidores AWS.
- [x] Deploy da branch `main` na AWS produção validado.
- [x] Deploy da branch `develop` na AWS staging validado.
- [x] `/health/` e Swagger acessíveis por HTTPS em ambos os ambientes durante a validação.
- [x] Rollback **de código** testado no staging e versão atual restaurada.
- [x] README atualizado com arquitetura, URLs e limitações conhecidas.
- [ ] Versionar uma configuração AWS reutilizável, sem arquivos secretos, e validar instalação nova.
- [ ] Testar restauração do backup em banco descartável e estabelecer cópia externa.
- [ ] Fazer revisão final de segurança e execução de `manage.py check --deploy` com configurações da AWS.
- [ ] Confirmar que segredos, arquivos `.env*` e dumps não foram publicados.
- [ ] Confirmar critérios de aceitação e enviar link do repositório à equipe da ONG.

## 11. Extra opcional — proposta de integração Asaas

**Não implementado.** Uma integração futura poderá relacionar uma cobrança à consulta, solicitar cobrança na API do Asaas e processar webhooks com verificação de autenticidade e idempotência. Credenciais ficariam exclusivamente no backend, e não seriam armazenados dados completos de cartão. Staging utilizaria ambiente de testes isolado de produção
