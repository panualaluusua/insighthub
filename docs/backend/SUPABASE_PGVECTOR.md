---
title: Supabase pgvector Integration
---

# Supabase pgvector Integration for InsightHub

This document describes the database schema and migration steps required to
store **content vectors** and **user profile vectors** in Supabase using the
[pgvector](https://github.com/pgvector/pgvector) extension.

> **Scope:** Task 12.2 – persistent VectorStore backend.

---

## 1 Enable `pgvector` Extension

```sql
-- Enable inside your project (executed once)
create extension if not exists pgvector;
```

Supabase exposes `pgvector` out-of-the-box; the above command is a safeguard
for local dev.

---

## 2 Table Definitions

### 2.1 `content_vectors`

| Column      | Type        | Constraints                 | Notes                                |
|-------------|------------|-----------------------------|--------------------------------------|
| id          | uuid        | primary key                 | Foreign key → `content.id` optional   |
| vector      | vector(768) | not null                    | 768-D embeddings (OpenAI/MPNet)       |
| created_at  | timestamptz | default `now()`             |                                        |
| updated_at  | timestamptz | default `now()`             | trigger updates on row change         |

```sql
create table if not exists content_vectors (
    id uuid primary key,
    vector vector(768) not null,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);
```

### 2.2 `user_vectors`

| Column      | Type        | Constraints                 | Notes                                |
|-------------|------------|-----------------------------|--------------------------------------|
| user_id     | uuid        | primary key                 | Supabase `auth.users.id`              |
| vector      | vector(768) | not null                    | current interest profile              |
| updated_at  | timestamptz | default `now()`             | trigger updates on row change         |

```sql
create table if not exists user_vectors (
    user_id uuid primary key references auth.users(id) on delete cascade,
    vector vector(768) not null,
    updated_at timestamptz default now()
);
```

> **Note:** Table names match the `SupabaseVectorStore` implementation in
> `src/storage/vector_store.py`.

---

## 3 Indexing & Similarity Search

To accelerate ANN similarity queries (future feature), create an
[HNSW](https://supabase.com/docs/guides/database/extensions/pgvector#usage)
index:

```sql
-- Top-k similarity for content recommendations
create index if not exists content_vectors_idx on content_vectors
using hnsw (vector vector_l2_ops);
```

For user vectors (less frequent), a regular ivfflat or exact index can be used
later.

---

## 4 Row-Level Security (RLS)

```sql
-- Allow only service role or owner to update their own vector
alter table user_vectors enable row level security;
create policy "Users can update own vector" on user_vectors
for update using (auth.uid() = user_id);
```

Content vectors are managed by internal services; RLS disabled by default.

---

## 5 Migrations

1. Create a migration file `20250703_add_pgvector_tables.sql` in your migrations
   folder.
2. Paste the SQL from sections 1–4.
3. Deploy via Supabase CLI:

```bash
supabase db reset   # dev only
supabase db push
```

---

## 6 Environment Configuration

Add to `.env` or Cursor MCP configuration:

```
SUPABASE_URL=<https://XXXX.supabase.co>
SUPABASE_SERVICE_KEY=<service_role_key>
```

No changes are needed in code – `VectorStore` factory auto-detects these.

---

## 7 Testing Strategy

* **Unit tests** use the default `InMemoryVectorStore`, so CI remains fast.
* **Integration tests** (optional) can set the env vars and run against
  Supabase's shadow DB.

---

## 8 Future Work

* Add Redis caching layer for hot vectors.
* Implement `delete_vector` methods.
* Expose similarity search endpoints.
