# Database Migrations

This directory contains Alembic database migrations for The Lariat Bible.

## Overview

Alembic is used to manage database schema changes in a version-controlled way. This allows you to:
- Track all database schema changes
- Upgrade or downgrade to any version
- Generate migrations automatically from model changes
- Maintain consistency across development, staging, and production environments

## Common Commands

### Create a new migration

After modifying your database models, generate a migration:

```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations

Upgrade to the latest version:

```bash
alembic upgrade head
```

Upgrade to a specific version:

```bash
alembic upgrade <revision_id>
```

### Rollback migrations

Downgrade one version:

```bash
alembic downgrade -1
```

Downgrade to a specific version:

```bash
alembic downgrade <revision_id>
```

Downgrade all the way:

```bash
alembic downgrade base
```

### View migration history

Show current revision:

```bash
alembic current
```

Show migration history:

```bash
alembic history
```

Show pending migrations:

```bash
alembic history --indicate-current
```

## Migration File Structure

```
migrations/
├── versions/          # Migration scripts
├── env.py            # Migration environment config
├── script.py.mako    # Template for new migrations
└── README.md         # This file
```

## Best Practices

1. **Always review auto-generated migrations** - Alembic's autogenerate is helpful but not perfect
2. **Test migrations both ways** - Always test upgrade and downgrade
3. **Use descriptive names** - Make migration messages clear and specific
4. **One logical change per migration** - Don't combine unrelated changes
5. **Commit migrations with code** - Keep migrations in version control with the code they support
6. **Never modify applied migrations** - Create a new migration instead
7. **Back up before migrating production** - Always backup before running migrations in production

## Environment-Specific Migrations

The migration system uses the `FLASK_ENV` environment variable to determine which database to migrate:

- `development` - Uses local development database
- `staging` - Uses staging database
- `production` - Uses production database

## Creating Your First Migration

When you create your first database models:

1. Import them in `migrations/env.py`
2. Update the `target_metadata` variable to point to your models' metadata
3. Run `alembic revision --autogenerate -m "Initial schema"`
4. Review the generated migration
5. Apply with `alembic upgrade head`

## Troubleshooting

### "Can't locate revision identified by..."
This usually means your database is out of sync. Check:
- Database connection is correct
- Migration files exist in versions/
- Database has alembic_version table

### Autogenerate doesn't detect changes
Make sure:
- Models are imported in env.py
- target_metadata is set correctly
- Database is at the current revision

### Migration fails halfway
- Check the migration file for errors
- Fix the migration
- Downgrade to before the failed migration
- Re-run the upgrade
