name: "supertokens-direct-db-cache-agent"
description: >
  Agent that bypasses the SuperTokens SDK and directly reads from Postgres tables
  (emailpassword_users, user_metadata, user_roles, user_last_active).
  It loads all user data (email, roles, metadata, last active) at startup,
  builds a local cache, and provides fast access without multiple SDK calls.

goals:
  - Bypass SuperTokens SDK entirely.
  - Create a PostgreSQL view combining all user info into a single query.
  - Load all user data on application startup.
  - Store users in a fast in-memory cache (dictionary or LRU cache).
  - Keep cache updated on user update/delete events.
  - Expose read-only API (or internal function) for querying users by ID/email.
  - Optional: prepare for distributed cache (Redis) later.

environment:
  language: python
  framework: fastapi
  database: postgresql
  cache: in-memory (@cached or functools.lru_cache)
  persistence: none (data reloaded on restart)

database_schema:
  tables:
    emailpassword_users:
      columns:
        - user_id (UUID, PK)
        - email (text)
        - time_joined (bigint)
        - password_hash (text)
    user_metadata:
      columns:
        - user_id (UUID, FK)
        - user_metadata (jsonb as text)
    user_roles:
      columns:
        - user_id (UUID, FK)
        - role (text)
    user_last_active:
      columns:
        - user_id (UUID, FK)
        - last_active_time (bigint)

database_view:
  name: user_full_view
  purpose: >
    Aggregate all user data into a single queryable entity for fast load.
  sql: |
    CREATE OR REPLACE VIEW user_full_view AS
    SELECT 
        e.user_id,
        e.email,
        e.time_joined,
        m.user_metadata::jsonb AS metadata,
        l.last_active_time,
        array_agg(r.role) AS roles
    FROM emailpassword_users e
    LEFT JOIN user_metadata m ON e.user_id = m.user_id
    LEFT JOIN user_last_active l ON e.user_id = l.user_id
    LEFT JOIN user_roles r ON e.user_id = r.user_id
    GROUP BY e.user_id, e.email, e.time_joined, m.user_metadata, l.last_active_time;

cache_design:
  cache_key: user_id
  data_model:
    user_id: str
    email: str
    metadata: dict
    roles: list[str]
    last_active: int
    time_joined: int
  load_strategy:
    on_startup:
      - Query all users from user_full_view.
      - Deserialize metadata JSON.
      - Build a dict[user_id → user_object].
  invalidation_strategy:
    on_user_update:
      - Requery single user from user_full_view by user_id.
      - Update local cache.
    on_user_delete:
      - Remove user_id from cache.
    fallback:
      - Full reload if mismatch or version drift detected.

api_endpoints:
  - GET /users
    description: Return all cached users.
  - GET /users/{user_id}
    description: Return cached user by ID.
  - POST /users/reload
    description: Force reload cache from database (admin-only).

implementation_plan:
  steps:
    - [ ] Define SQLAlchemy Core models (or use raw SQL).
    - [ ] Create user_full_view via Alembic migration.
    - [ ] Implement `UserCache` singleton class:
        - Methods: `load_all()`, `get_user(id)`, `reload_user(id)`, `remove_user(id)`.
    - [ ] Hook into FastAPI startup event:
        - Call `UserCache.load_all()`.
    - [ ] Optionally use `@lru_cache` or similar for reads.
    - [ ] Add endpoints to expose cached user data.
  notes:
    - Cache is local only, fine for single instance.
    - In multi-instance setups, use Redis pub/sub for cache invalidation.
    - Use DataLoader batching if integrating with GraphQL later.

future_enhancements:
  - Use Redis for distributed caching.
  - Add NOTIFY/LISTEN triggers in Postgres for cache updates.
  - Add TTL-based background refresh.
  - Use Pydantic models for strict typing.
  - Integrate with role-based authorization module.

output_expectation:
  - Python/FastAPI codebase with:
    - user_full_view.sql file
    - cache.py (UserCache class)
    - models.py (ORM or dataclass)
    - main.py (startup logic)
  - Optional test to verify full cache load.
