
# import sqlite3
# from datetime import datetime

# from sqlalchemy import inspect, text

# from app import create_app
# from app.extensions import db


# SOURCE_DB = "instance/cipher.db"

# TABLE_COLUMNS = {
#     "users": [
#         "id", "username", "email", "password", "is_admin",
#         "created_at", "xp", "level", "rank",
#         "missions_completed", "badges",
#     ],
#     "missions": [
#         "id", "title", "description", "difficulty",
#         "reward_xp", "is_locked", "created_at",
#     ],
#     "puzzles": [
#         "id", "mission_id", "question", "answer", "hint",
#         "reward_xp", "title", "description", "clue", "image",
#         "order", "xp", "max_attempts", "created_at",
#     ],
#     "puzzle_progress": [
#         "id", "user_id", "mission_id", "puzzle_id", "completed",
#         "attempts", "locked_until", "retry_count",
#         "attempts_reset_at", "attempts_remaining",
#         "reset_available_at",
#     ],
#     "mission_completions": [
#         "id", "user_id", "mission_id", "completed_at", "xp_earned",
#     ],
# }

# EXPECTED_COUNTS = {
#     "users": 6,
#     "missions": 7,
#     "puzzles": 38,
#     "puzzle_progress": 26,
#     "mission_completions": 4,
# }

# INSERT_ORDER = [
#     "users",
#     "missions",
#     "puzzles",
#     "puzzle_progress",
#     "mission_completions",
# ]

# DATETIME_COLUMNS = {
#     "created_at",
#     "completed_at",
#     "locked_until",
#     "attempts_reset_at",
#     "reset_available_at",
# }

# BOOLEAN_COLUMNS = {
#     "is_admin",
#     "is_locked",
#     "completed",
# }


# def normalize_value(column, value):
#     if value is None:
#         return None

#     if column in BOOLEAN_COLUMNS:
#         return bool(value)

#     if column in DATETIME_COLUMNS and isinstance(value, str):
#         try:
#             return datetime.fromisoformat(value)
#         except ValueError:
#             return value

#     return value


# def load_source_data(source):
#     source_data = {}

#     for table, columns in TABLE_COLUMNS.items():
#         actual_columns = {
#             row["name"]
#             for row in source.execute(
#                 f'PRAGMA table_info("{table}")'
#             ).fetchall()
#         }

#         missing = set(columns) - actual_columns

#         if missing:
#             raise RuntimeError(
#                 f"SQLite table '{table}' is missing columns: "
#                 f"{sorted(missing)}"
#             )

#         column_sql = ", ".join(f'"{column}"' for column in columns)

#         rows = source.execute(
#             f'SELECT {column_sql} FROM "{table}" ORDER BY id'
#         ).fetchall()

#         source_data[table] = [
#             {
#                 column: normalize_value(column, row[column])
#                 for column in columns
#             }
#             for row in rows
#         ]

#         expected = EXPECTED_COUNTS[table]

#         if len(source_data[table]) != expected:
#             raise RuntimeError(
#                 f"Unexpected SQLite count for '{table}': "
#                 f"expected {expected}, found {len(source_data[table])}. "
#                 "Migration stopped without inserting data."
#             )

#     return source_data


# def verify_target_schema(connection):
#     inspector = inspect(connection)

#     for table, columns in TABLE_COLUMNS.items():
#         target_columns = {
#             column["name"]
#             for column in inspector.get_columns(table)
#         }

#         missing = set(columns) - target_columns

#         if missing:
#             raise RuntimeError(
#                 f"PostgreSQL table '{table}' is missing columns: "
#                 f"{sorted(missing)}"
#             )


# def verify_target_is_empty(connection):
#     for table in INSERT_ORDER:
#         count = connection.execute(
#             text(f'SELECT COUNT(*) FROM "{table}"')
#         ).scalar_one()

#         if count != 0:
#             raise RuntimeError(
#                 f"Migration stopped: PostgreSQL table '{table}' "
#                 f"already contains {count} records. "
#                 "No records were inserted by this migration."
#             )


# def insert_table(connection, table, rows):
#     if not rows:
#         return

#     columns = TABLE_COLUMNS[table]

#     column_sql = ", ".join(f'"{column}"' for column in columns)
#     placeholders = ", ".join(f":{column}" for column in columns)

#     statement = text(
#         f'INSERT INTO "{table}" ({column_sql}) '
#         f"VALUES ({placeholders})"
#     )

#     connection.execute(statement, rows)


# def reset_id_sequence(connection, table):
#     max_id = connection.execute(
#         text(f'SELECT MAX(id) FROM "{table}"')
#     ).scalar_one()

#     sequence_name = connection.execute(
#         text("SELECT pg_get_serial_sequence(:table_name, 'id')"),
#         {"table_name": table},
#     ).scalar_one()

#     if sequence_name is None:
#         raise RuntimeError(
#             f"No PostgreSQL ID sequence found for '{table}'. "
#             "Please inspect the table before proceeding."
#         )

#     if max_id is None:
#         last_value = 1
#         is_called = False
#     else:
#         last_value = max_id
#         is_called = True

#     connection.execute(
#         text("""
#             SELECT setval(
#                 CAST(:sequence_name AS regclass),
#                 :last_value,
#                 :is_called
#             )
#         """),
#         {
#             "sequence_name": sequence_name,
#             "last_value": last_value,
#             "is_called": is_called,
#         },
#     )


# def verify_migrated_data(connection, source_data):
#     print("\n--- Verifying PostgreSQL data ---")

#     for table in INSERT_ORDER:
#         expected_rows = source_data[table]

#         actual_count = connection.execute(
#             text(f'SELECT COUNT(*) FROM "{table}"')
#         ).scalar_one()

#         expected_count = len(expected_rows)

#         print(
#             f"{table}: {actual_count} records "
#             f"(expected {expected_count})"
#         )

#         if actual_count != expected_count:
#             raise RuntimeError(
#                 f"Record count mismatch in '{table}'."
#             )

#         expected_ids = sorted(row["id"] for row in expected_rows)

#         actual_ids = connection.execute(
#             text(f'SELECT id FROM "{table}" ORDER BY id')
#         ).scalars().all()

#         if list(actual_ids) != expected_ids:
#             raise RuntimeError(
#                 f"ID verification failed for '{table}'."
#             )

#     # Explicitly preserve the known orphan progress record.
#     orphan_progress = connection.execute(
#         text("""
#             SELECT id, user_id, mission_id, puzzle_id
#             FROM puzzle_progress
#             WHERE id = 14
#         """)
#     ).first()

#     if orphan_progress is None:
#         raise RuntimeError(
#             "Expected progress record ID 14 was not found."
#         )

#     if (
#         orphan_progress.user_id != 1
#         or orphan_progress.mission_id != 2
#         or orphan_progress.puzzle_id != 8
#     ):
#         raise RuntimeError(
#             "Progress record ID 14 does not match the source reference."
#         )

#     print("Progress record 14 preserved with puzzle_id 8.")


# def main():
#     app = create_app()

#     # Open the original SQLite database in read-only mode.
#     source = sqlite3.connect(
#         f"file:{SOURCE_DB}?mode=ro",
#         uri=True,
#     )
#     source.row_factory = sqlite3.Row

#     try:
#         source_data = load_source_data(source)

#         print("--- Source SQLite counts ---")
#         for table in INSERT_ORDER:
#             print(f"{table}: {len(source_data[table])}")

#         with app.app_context():
#             # A single PostgreSQL transaction for all inserts.
#             with db.engine.begin() as connection:
#                 verify_target_schema(connection)
#                 verify_target_is_empty(connection)

#                 for table in INSERT_ORDER:
#                     insert_table(
#                         connection,
#                         table,
#                         source_data[table],
#                     )
#                     print(
#                         f"Inserted {len(source_data[table])} "
#                         f"records into {table}"
#                     )

#                 for table in INSERT_ORDER:
#                     reset_id_sequence(connection, table)

#                 verify_migrated_data(connection, source_data)

#         print("\nSUCCESS: Migration completed and committed.")
#         print("Original SQLite database was opened read-only.")

#     finally:
#         source.close()


# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as error:
#         print("\nMIGRATION FAILED:", error)
#         print(
#             "If the failure occurred during the PostgreSQL transaction, "
#             "its inserts were rolled back."
#         )
#         raise


import os
import sqlite3
from sqlalchemy import create_engine, text

SOURCE_DB = "instance/cipher.db"

MISSION_COLUMNS = [
    "id",
    "title",
    "description",
    "difficulty",
    "reward_xp",
    "is_locked",
    "created_at",
]

PUZZLE_COLUMNS = [
    "id",
    "mission_id",
    "title",
    "description",
    "clue",
    "question",
    "answer",
    "image",
    "order",
    "xp",
    "max_attempts",
    "created_at",
]


def main():
    if not os.path.exists(SOURCE_DB):
        raise FileNotFoundError(
            f"Source database not found: {SOURCE_DB}"
        )

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set.")

    if "sslmode=" not in database_url:
        database_url += (
            "&" if "?" in database_url else "?"
        ) + "sslmode=require"

    source = sqlite3.connect(SOURCE_DB)
    source.row_factory = sqlite3.Row

    engine = create_engine(
        database_url,
        connect_args={"connect_timeout": 10},
    )

    try:
        missions = source.execute(
            "SELECT * FROM missions ORDER BY id"
        ).fetchall()

        puzzles = source.execute(
            'SELECT * FROM puzzles ORDER BY id'
        ).fetchall()

        if len(missions) != 7 or len(puzzles) != 38:
            raise RuntimeError(
                f"Unexpected source counts: "
                f"{len(missions)} missions, "
                f"{len(puzzles)} puzzles. "
                "Expected 7 missions and 38 puzzles."
            )

        for row in missions:
            missing = set(MISSION_COLUMNS) - set(row.keys())
            if missing:
                raise RuntimeError(
                    f"Missing mission columns: {sorted(missing)}"
                )

        for row in puzzles:
            missing = set(PUZZLE_COLUMNS) - set(row.keys())
            if missing:
                raise RuntimeError(
                    f"Missing puzzle columns: {sorted(missing)}"
                )

        with engine.begin() as conn:
            mission_count = conn.execute(
                text("SELECT COUNT(*) FROM missions")
            ).scalar_one()

            puzzle_count = conn.execute(
                text("SELECT COUNT(*) FROM puzzles")
            ).scalar_one()

            if mission_count != 0 or puzzle_count != 0:
                raise RuntimeError(
                    "Migration stopped safely. "
                    f"Render already contains {mission_count} missions "
                    f"and {puzzle_count} puzzles. "
                    "No rows were inserted."
                )

            target_mission_columns = {
                column["name"]
                for column in
                __import__("sqlalchemy").inspect(
                    conn
                ).get_columns("missions")
            }

            target_puzzle_columns = {
                column["name"]
                for column in
                __import__("sqlalchemy").inspect(
                    conn
                ).get_columns("puzzles")
            }

            if not set(MISSION_COLUMNS).issubset(
                target_mission_columns
            ):
                raise RuntimeError(
                    "Render missions schema does not match."
                )

            if not set(PUZZLE_COLUMNS).issubset(
                target_puzzle_columns
            ):
                raise RuntimeError(
                    "Render puzzles schema does not match."
                )

            for row in missions:
                values = {
                    column: row[column]
                    for column in MISSION_COLUMNS
                }

                values["is_locked"] = bool(values["is_locked"])

                conn.execute(
                    text(
                        "INSERT INTO missions "
                        "(id, title, description, difficulty, "
                        "reward_xp, is_locked, created_at) "
                        "VALUES (:id, :title, :description, "
                        ":difficulty, :reward_xp, :is_locked, "
                        ":created_at)"
                    ),
                    values,
                )

            for row in puzzles:
                values = {
                    column: row[column]
                    for column in PUZZLE_COLUMNS
                }

                conn.execute(
                    text(
                        'INSERT INTO puzzles '
                        '(id, mission_id, title, description, clue, '
                        'question, answer, image, "order", xp, '
                        'max_attempts, created_at) '
                        'VALUES (:id, :mission_id, :title, '
                        ':description, :clue, :question, :answer, '
                        ':image, :order, :xp, :max_attempts, '
                        ':created_at)'
                    ),
                    values,
                )

            conn.execute(
                text(
                    "SELECT setval("
                    "pg_get_serial_sequence('missions', 'id'), "
                    "COALESCE((SELECT MAX(id) FROM missions), 1), "
                    "EXISTS(SELECT 1 FROM missions)"
                    ")"
                )
            )

            conn.execute(
                text(
                    "SELECT setval("
                    "pg_get_serial_sequence('puzzles', 'id'), "
                    "COALESCE((SELECT MAX(id) FROM puzzles), 1), "
                    "EXISTS(SELECT 1 FROM puzzles)"
                    ")"
                )
            )

            final_missions = conn.execute(
                text("SELECT COUNT(*) FROM missions")
            ).scalar_one()

            final_puzzles = conn.execute(
                text("SELECT COUNT(*) FROM puzzles")
            ).scalar_one()

            if final_missions != 7 or final_puzzles != 38:
                raise RuntimeError(
                    "Final verification failed; transaction will roll back."
                )

        print("Migration successful!")
        print(f"Missions migrated: {len(missions)}")
        print(f"Puzzles migrated: {len(puzzles)}")
        print("Existing online users were not modified.")

    finally:
        source.close()
        engine.dispose()


if __name__ == "__main__":
    main()
