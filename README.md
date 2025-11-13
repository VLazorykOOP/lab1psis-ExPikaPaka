# Docker Lab: FastAPI + Postgres + Adminer + Web UI

## Запуск
docker compose up -d --build

### Сервіси:
- API/UI: [http://localhost:8000](http://localhost:8000)
- Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Adminer: [http://localhost:8080](http://localhost:8080)

### Параметри входу в Adminer
- System: PostgreSQL
- Server: db
- User: appuser
- Password: apppass
- Database: appdb

Зупинка:
docker compose down

Повне очищення (дані БД зітруться):
docker compose down -v
