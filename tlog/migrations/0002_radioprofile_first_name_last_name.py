"""
Миграция: Добавление полей first_name и last_name в RadioProfile (Django 5.2)
Проверяет существование колонок перед добавлением
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tlog', '0001_initial'),
    ]

    operations = [
        # Добавляем поле first_name только если оно не существует
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT FROM information_schema.columns
                    WHERE table_name = 'tlog_radioprofile'
                    AND column_name = 'first_name'
                ) THEN
                    ALTER TABLE tlog_radioprofile ADD COLUMN first_name VARCHAR(100) DEFAULT '';
                END IF;
            END $$;
            """,
            reverse_sql="""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT FROM information_schema.columns
                    WHERE table_name = 'tlog_radioprofile'
                    AND column_name = 'first_name'
                ) THEN
                    ALTER TABLE tlog_radioprofile DROP COLUMN first_name;
                END IF;
            END $$;
            """,
        ),
        # Добавляем поле last_name только если оно не существует
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT FROM information_schema.columns
                    WHERE table_name = 'tlog_radioprofile'
                    AND column_name = 'last_name'
                ) THEN
                    ALTER TABLE tlog_radioprofile ADD COLUMN last_name VARCHAR(100) DEFAULT '';
                END IF;
            END $$;
            """,
            reverse_sql="""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT FROM information_schema.columns
                    WHERE table_name = 'tlog_radioprofile'
                    AND column_name = 'last_name'
                ) THEN
                    ALTER TABLE tlog_radioprofile DROP COLUMN last_name;
                END IF;
            END $$;
            """,
        ),
    ]
