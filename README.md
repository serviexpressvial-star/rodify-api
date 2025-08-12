# Rodify API (SQLite) — listo para usar y desplegar

Incluye:
- **SQLite** (persistencia real, archivo `rodify.db` se genera automáticamente).
- **Seed** de datos: 1 cliente y 1 técnico listos.
- **Tarifario** por zona y horario nocturno (22:00–06:00) + feriado.
- **render.yaml** y **Procfile** para desplegar en Render.

## Cómo correr local
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# abre http://127.0.0.1:8000/docs
```

Usuarios demo (consulta en runtime):
```
GET /system/demo-users
```

Flujo típico:
1. **Cotizar** `POST /services/quote`
2. **Crear servicio** `POST /services`
3. **Ver servicio** `GET /services/{code}`
4. **Asignar técnico** `POST /services/{code}/accept?technician_id=...`
5. **Actualizar estado** `POST /services/{code}/status?status=en_route&notes=...`
6. **Disponibles** `GET /technicians/available?zone=ciudad`

## Despliegue en Render (rápido)
1. Sube este folder a un repo (GitHub/GitLab).
2. En Render → New Web Service → conecta el repo.
3. Render detecta `render.yaml` y crea el servicio.
4. Espera el deploy y prueba `https://<tu-app>.onrender.com/health`.

> El `DATABASE_URL` por defecto usa SQLite; Render lo soporta. Si luego quieres Postgres, cambia `DATABASE_URL` y listo.

## Notas
- Seguridad/auth mínima (para MVP). Antes de producción real, agrega autenticación (Supabase Auth o JWT) y control de roles.
- Tarifas en tabla `pricing_rules` (modifícalas desde la DB o crea un endpoint admin).

¡Listo para usar!
