# Supabase Integration

This document outlines how InsightHub integrates with Supabase for data storage and security.

## Overview

Supabase serves as the primary backend-as-a-service for InsightHub, providing a PostgreSQL database, authentication, and row-level security (RLS) to ensure data is stored securely and accessed only by authorized users.

## Connection

The connection to Supabase is managed by the `SupabaseClient` class, located in `src/reddit_weekly_top/supabase_client.py`. This class uses the `SUPABASE_URL` and `SUPABASE_ANON_KEY` environment variables to establish a connection to the Supabase project.

## Data Storage

The `StorageNode` in the orchestrator (`src/orchestrator/nodes/storage.py`) is responsible for persisting the processed content from Reddit and YouTube into the Supabase database. The exact table structure should be documented here as the project evolves.

## Security: Row-Level Security (RLS)

A key aspect of the Supabase integration is the use of Row-Level Security (RLS) policies to control access to the data. These policies are defined and managed in `src/rls_implementation.py`.

The RLS policies ensure that users can only access their own data. The tests in `src/test_rls_policies.py` are designed to verify the correctness of these policies.

## Setup

To enable the Supabase integration, you must set the following environment variables in your `.env` file:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```
