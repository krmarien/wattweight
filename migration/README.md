# Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema versioning and migrations.

## Overview

Migrations are version-controlled SQL/Python scripts that facilitate controlled changes to the database schema. They allow you to:
- Track schema changes over time
- Roll back changes if needed
- Share schema updates with your team
- Automate database updates in production

## Migration Directory Structure

```
migration/
├── alembic/
│   └── versions/          # Individual migration files
├── env.py                 # Alembic environment configuration
└── script.py.mako         # Migration template
```

## Creating a New Migration

### Using Wattweight CLI (Recommended)

Create migrations directly from the CLI:

```bash
# Auto-generate migration from model changes
wattweight db migrate "Add new field to Device"
```

### Using Alembic Directly

If you prefer using Alembic directly:

```bash
# From the project root
alembic revision --autogenerate -m "Add new field to Device"
```

This will:
1. Compare current models with the database schema
2. Generate a migration file with the detected changes
3. Create it in `migration/versions/`

### Manual

For more control or complex migrations:

```bash
alembic revision -m "Custom migration description"
```

This creates an empty migration template you can edit.

## Reviewing Migrations

Before applying, review the generated migration in `migration/versions/`:

```python
# Example: 001_add_device_field.py

def upgrade():
    """Add new field to device table."""
    op.add_column('device', sa.Column('new_field', sa.String(), nullable=False))

def downgrade():
    """Remove new field from device table."""
    op.drop_column('device', 'new_field')
```

Edit the migration if needed to ensure it's correct.

## Upgrading the Database

### Using Wattweight CLI (Recommended)

```bash
# Upgrade to the latest version
wattweight db upgrade

# With verbose logging to see SQL statements
wattweight -vv db upgrade
```

### Using Alembic Directly

```bash
alembic upgrade head
```

```python
from wattweight import Database
from wattweight.core.migration import MigrationManager

with Database() as db:
    manager = MigrationManager(db)
    manager.upgrade()
```

## Checking Migration Status

```bash
alembic current      # Show current revision
alembic history      # Show all revisions
```

## Rollback (Downgrade)

To roll back to a previous version:

```bash
alembic downgrade -1  # Go back one version
alembic downgrade <revision_id>  # Go to specific version
```

## Workflow

1. **Modify your models** in `src/wattweight/model/`
2. **Generate migration** with `wattweight db migrate "Add new field"`
3. **Review the migration** file in `migration/versions/`
4. **Test locally** with `wattweight db upgrade`
5. **Commit** the migration file to version control
6. **Deploy** - run `wattweight db upgrade` on the target database

## Best Practices

- ✅ Generate migrations immediately after model changes
- ✅ Always review generated migrations before deploying
- ✅ Use descriptive migration messages
- ✅ Commit migrations with your code changes
- ✅ Test migrations in development/staging first
- ❌ Never manually edit the database schema - always use migrations
- ❌ Don't skip migrations in production

## Troubleshooting

### "Can't upgrade database"

Make sure:
1. Database path exists and is writable
2. Alembic is installed: `pip install alembic`
3. All models are imported in `migration/env.py`

### "Migration conflicts"

If two developers create migrations simultaneously:
1. Review both migration files
2. Merge if necessary, creating a new migration if needed
3. Run `alembic downgrade base` then `alembic upgrade head` to test

### Database is newer than code

If the database somehow got upgraded without migrations tracked:

```bash
# Mark the current state as the baseline
alembic stamp head
```

## Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Database Versioning Best Practices](https://www.liquibase.org/get-started/best-practices)
