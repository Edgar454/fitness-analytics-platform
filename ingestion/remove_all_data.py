from sqlalchemy import text

from src.config import Config
from src.database import RDSConnector


db_connector = RDSConnector(
    Config.SQLALCHEMY_DATABASE_URI,
    connect_args=Config.get_ssl_connect_args(),
)


async def remove_all_data_in_db(db_connector: RDSConnector):
    async with db_connector.session() as db:
        result = await db.execute(
            text("""
                SELECT string_agg(
                    format('%I.%I', schemaname, tablename),
                    ', '
                )
                FROM pg_tables
                WHERE schemaname = 'public';
            """)
        )

        tables = result.scalar()

        if tables:
            await db.execute(
                text(
                    f"TRUNCATE TABLE {tables} "
                    "RESTART IDENTITY CASCADE;"
                )
            )

        await db.commit()

if __name__ == "__main__":
    import asyncio

    asyncio.run(remove_all_data_in_db(db_connector))
    print("All data removed from the database.")