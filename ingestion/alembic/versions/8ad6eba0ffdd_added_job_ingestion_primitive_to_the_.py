"""Added job ingestion primitive to the database

Revision ID: 8ad6eba0ffdd
Revises: f85ff0b4fbef
Create Date: 2026-09-01 11:24:26.235870

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8ad6eba0ffdd"
down_revision: Union[str, Sequence[str], None] = "f85ff0b4fbef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ------------------------------------------------------------------
    # Ingestion schema
    # ------------------------------------------------------------------

    op.execute("CREATE SCHEMA IF NOT EXISTS ingestion")

    # ------------------------------------------------------------------
    # State transition lookup table
    # ------------------------------------------------------------------

    op.create_table(
        "job_state_transitions",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        # String instead of JobStatus enum because this column also
        # supports the wildcard value "ANY".
        sa.Column(
            "from_state",
            sa.String(length=20),
            nullable=False,
        ),

        sa.Column(
            "event_type",
            sa.Enum(
                "CREATED",
                "PROCESSING_STARTED",
                "COMPLETED",
                "FAILED",
                "RETRY",
                name="jobeventtype",
            ),
            nullable=False,
        ),

        sa.Column(
            "to_state",
            sa.Enum(
                "QUEUED",
                "PROCESSING",
                "COMPLETED",
                "FAILED",
                name="jobstatus",
            ),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "from_state",
            "event_type",
            name="uq_job_state_transition",
        ),

        schema="ingestion",
    )

    # ------------------------------------------------------------------
    # Jobs
    # ------------------------------------------------------------------

    op.create_table(
        "jobs",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "connector",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.Enum(
                "QUEUED",
                "PROCESSING",
                "COMPLETED",
                "FAILED",
                name="jobstatus",
            ),
            nullable=False,
        ),

        sa.Column(
            "attempt_count",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "records_processed",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "locked_until",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "error",
            sa.Text(),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["fitness.users.id"],
        ),

        sa.PrimaryKeyConstraint("id"),

        schema="ingestion",
    )

    # ------------------------------------------------------------------
    # Job events
    # ------------------------------------------------------------------

    op.create_table(
        "job_events",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "job_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "event_type",
            sa.Enum(
                "CREATED",
                "PROCESSING_STARTED",
                "COMPLETED",
                "FAILED",
                "RETRY",
                name="jobeventtype",
            ),
            nullable=False,
        ),

        sa.Column(
            "source",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "error",
            sa.Text(),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(
            ["job_id"],
            ["ingestion.jobs.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),

        schema="ingestion",
    )

    # ------------------------------------------------------------------
    # Existing fitness schema changes detected by autogenerate
    # ------------------------------------------------------------------

    op.create_unique_constraint(
        "uq_daily_nutrition_user_date",
        "daily_nutrition",
        ["user_id", "date"],
        schema="fitness",
    )

    op.add_column(
        "users",
        sa.Column(
            "last_active",
            sa.DateTime(),
            nullable=True,
        ),
        schema="fitness",
    )

    op.drop_column(
        "users",
        "is_active",
        schema="fitness",
    )

    # ------------------------------------------------------------------
    # Seed state transition rules
    # ------------------------------------------------------------------

    op.execute(
        """
        INSERT INTO ingestion.job_state_transitions
            (from_state, event_type, to_state)
        VALUES
            ('ANY',        'CREATED',            'QUEUED'),
            ('QUEUED',     'PROCESSING_STARTED', 'PROCESSING'),
            ('PROCESSING', 'COMPLETED',          'COMPLETED'),
            ('PROCESSING', 'FAILED',             'FAILED'),
            ('FAILED',     'RETRY',              'QUEUED')
        """
    )

    # ------------------------------------------------------------------
    # Job event transition function
    # ------------------------------------------------------------------

    op.execute(
        """
        CREATE OR REPLACE FUNCTION ingestion.add_job_event(
            p_job_id INTEGER,
            p_event_type TEXT,
            p_source TEXT,
            p_message TEXT DEFAULT NULL,
            p_error TEXT DEFAULT NULL,
            p_records_processed INTEGER DEFAULT NULL,
            p_locked_until TIMESTAMPTZ DEFAULT NULL
        )
        RETURNS VOID
        LANGUAGE plpgsql
        AS $$
        DECLARE
            current_state TEXT;
            new_state TEXT;
        BEGIN

            -- ----------------------------------------------------------
            -- Lock the job.
            --
            -- This serializes events for the same job and prevents
            -- concurrent workers from transitioning it simultaneously.
            -- ----------------------------------------------------------

            SELECT status::TEXT
            INTO current_state
            FROM ingestion.jobs
            WHERE id = p_job_id
            FOR UPDATE;

            IF current_state IS NULL THEN
                RAISE EXCEPTION
                    'Job % does not exist',
                    p_job_id;
            END IF;


            -- ----------------------------------------------------------
            -- Resolve the next state.
            --
            -- The transition table is the source of truth.
            --
            -- An explicit transition takes precedence over an ANY
            -- transition if both exist.
            -- ----------------------------------------------------------

            SELECT to_state::TEXT
            INTO new_state
            FROM ingestion.job_state_transitions
            WHERE event_type::TEXT = p_event_type
              AND (
                    from_state = current_state
                    OR from_state = 'ANY'
                  )
            ORDER BY
                CASE
                    WHEN from_state = current_state THEN 0
                    ELSE 1
                END
            LIMIT 1;

            IF new_state IS NULL THEN
                RAISE EXCEPTION
                    'Invalid state transition: % + %',
                    current_state,
                    p_event_type;
            END IF;


            -- ----------------------------------------------------------
            -- Append immutable event.
            -- ----------------------------------------------------------

            INSERT INTO ingestion.job_events (
                job_id,
                event_type,
                source,
                created_at,
                message,
                error
            )
            VALUES (
                p_job_id,
                p_event_type::jobeventtype,
                p_source,
                NOW(),
                p_message,
                p_error
            );


            -- ----------------------------------------------------------
            -- Update job snapshot.
            -- ----------------------------------------------------------

            UPDATE ingestion.jobs
            SET

                -- New state resolved from transition table.
                status = new_state::jobstatus,


                -- Update record count when supplied.
                records_processed = COALESCE(
                    p_records_processed,
                    records_processed
                ),


                -- First processing attempt.
                started_at = CASE
                    WHEN p_event_type = 'PROCESSING_STARTED'
                        THEN NOW()
                    ELSE started_at
                END,


                -- Completion timestamp.
                --
                -- A retry resets the previous completion timestamp.
                completed_at = CASE
                    WHEN p_event_type = 'COMPLETED'
                        THEN NOW()

                    WHEN p_event_type = 'RETRY'
                        THEN NULL

                    ELSE completed_at
                END,


                -- Worker lock lifecycle.
                locked_until = CASE
                    WHEN p_event_type = 'PROCESSING_STARTED'
                        THEN p_locked_until

                    WHEN p_event_type IN (
                        'COMPLETED',
                        'FAILED',
                        'RETRY'
                    )
                        THEN NULL

                    ELSE locked_until
                END,


                -- Number of processing attempts.
                --
                -- attempt_count = 1 means the first worker attempt.
                -- attempt_count = 2 means the second attempt, etc.
                attempt_count = CASE
                    WHEN p_event_type = 'PROCESSING_STARTED'
                        THEN attempt_count + 1

                    ELSE attempt_count
                END,


                -- Error lifecycle.
                error = CASE
                    WHEN p_event_type = 'FAILED'
                        THEN p_error

                    WHEN p_event_type = 'RETRY'
                        THEN NULL

                    ELSE error
                END

            WHERE id = p_job_id;

        END;
        $$;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    # ------------------------------------------------------------------
    # Existing fitness schema changes
    # ------------------------------------------------------------------

    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.BOOLEAN(),
            autoincrement=False,
            nullable=False,
        ),
        schema="fitness",
    )

    op.drop_column(
        "users",
        "last_active",
        schema="fitness",
    )

    op.drop_constraint(
        "uq_daily_nutrition_user_date",
        "daily_nutrition",
        schema="fitness",
        type_="unique",
    )

    # ------------------------------------------------------------------
    # Remove ingestion function
    # ------------------------------------------------------------------

    op.execute(
        """
        DROP FUNCTION IF EXISTS ingestion.add_job_event(
            INTEGER,
            TEXT,
            TEXT,
            TEXT,
            TEXT,
            INTEGER,
            TIMESTAMPTZ
        )
        """
    )

    # ------------------------------------------------------------------
    # Remove ingestion tables
    # ------------------------------------------------------------------

    op.drop_table(
        "job_events",
        schema="ingestion",
    )

    op.drop_table(
        "jobs",
        schema="ingestion",
    )

    op.drop_table(
        "job_state_transitions",
        schema="ingestion",
    )

    # ------------------------------------------------------------------
    # Remove ingestion schema
    # ------------------------------------------------------------------

    op.execute(
        "DROP SCHEMA IF EXISTS ingestion CASCADE"
    )