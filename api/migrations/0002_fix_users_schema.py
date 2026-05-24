from django.db import migrations


class Migration(migrations.Migration):
    """
    Adds columns that may be missing from a pre-existing `users` table
    (e.g. created by a Laravel project sharing the same MySQL database).
    Uses IF NOT EXISTS so it is safe to run on a fresh schema too.
    """

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login DATETIME(6) NULL",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_superuser TINYINT(1) NOT NULL DEFAULT 0",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_staff TINYINT(1) NOT NULL DEFAULT 0",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active TINYINT(1) NOT NULL DEFAULT 1",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at DATETIME(6) NULL",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20) NULL",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(50) NULL",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
