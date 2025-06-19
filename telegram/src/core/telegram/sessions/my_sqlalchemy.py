from typing import Any, Dict, Optional, Tuple, Union

import sqlalchemy as sql
from sqlalchemy import (
    BigInteger,
    Column,
    Integer,
    LargeBinary,
    String,
    and_,
    func,
    orm,
    select,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.scoping import scoped_session

from .core import AlchemyCoreSession
from .core_postgres import AlchemyPostgresCoreSession
from .orm import AlchemySession

LATEST_VERSION = 2


class AlchemySessionContainer:
    def __init__(
        self,
        engine: Union[sql.engine.Engine, str] = None,
        session: Optional[Union[orm.Session, scoped_session, bool]] = None,
        table_prefix: str = "",
        table_base: Optional[declarative_base] = None,
        manage_tables: bool = True,
    ) -> None:
        if isinstance(engine, str):
            engine = sql.create_engine(engine)

        self.db_engine = engine
        if session is None:
            db_factory = orm.sessionmaker(bind=self.db_engine)
            self.db = orm.scoping.scoped_session(db_factory)
        elif not session:
            self.db = None
        else:
            self.db = session

        table_base = table_base or declarative_base()
        (
            self.Version,
            self.Session,
            self.Entity,
            self.SentFile,
            self.UpdateState,
            self.Account,
        ) = self.create_table_classes(self.db, table_prefix, table_base)
        self.alchemy_session_class = AlchemySession
        if not self.db:
            # Implicit core mode if there's no ORM session.
            self.core_mode = True

        if manage_tables:
            if not self.db:
                raise ValueError("Can't manage tables without an ORM session.")
            table_base.metadata.bind = self.db_engine
            if not self.db_engine.dialect.has_table(
                self.db_engine, self.Version.__tablename__
            ):
                table_base.metadata.create_all()
                self.db.add(self.Version(version=LATEST_VERSION))
                self.db.commit()
            else:
                self.check_and_upgrade_database()

    @property
    def core_mode(self) -> bool:
        return self.alchemy_session_class != AlchemySession

    @core_mode.setter
    def core_mode(self, val: bool) -> None:
        if val:
            if self.db_engine.dialect.name == "mysql":
                self.alchemy_session_class = "AlchemyMySQLCoreSession"
            elif self.db_engine.dialect.name == "postgresql":
                self.alchemy_session_class = AlchemyPostgresCoreSession
            elif self.db_engine.dialect.name == "sqlite":
                self.alchemy_session_class = "AlchemySQLiteCoreSession"
            else:
                self.alchemy_session_class = AlchemyCoreSession
        else:
            if not self.db:
                raise ValueError("Can't use ORM mode without an ORM session.")
            self.alchemy_session_class = AlchemySession

    @staticmethod
    def create_table_classes(
        db: scoped_session, prefix: str, base: declarative_base
    ) -> Tuple[Any, Any, Any, Any, Any, Any]:
        qp = db.query_property() if db else None

        class Version(base):
            query = qp
            __tablename__ = f"{prefix}version"
            __table_args__ = {"extend_existing": True}
            version = Column(Integer, primary_key=True)

            def __str__(self):
                return f"Version('{self.version}')"

        class Session(base):
            query = qp
            __tablename__ = f"{prefix}sessions"
            __table_args__ = {"extend_existing": True}

            session_id = Column(String(20), primary_key=True)
            dc_id = Column(Integer, primary_key=True)
            server_address = Column(String(255))
            port = Column(Integer)
            auth_key = Column(LargeBinary)

            def __str__(self):
                return "Session('{}', {}, '{}', {}, {})".format(
                    self.session_id,
                    self.dc_id,
                    self.server_address,
                    self.port,
                    self.auth_key,
                )

        class Entity(base):
            query = qp
            __tablename__ = f"{prefix}entities"
            __table_args__ = {"extend_existing": True}

            session_id = Column(String(20), primary_key=True)
            id = Column(BigInteger, primary_key=True)
            hash = Column(BigInteger, nullable=False)
            username = Column(String(32))
            phone = Column(BigInteger)
            name = Column(String(255))

            def __str__(self):
                return "Entity('{}', {}, {}, '{}', '{}', '{}')".format(
                    self.session_id,
                    self.id,
                    self.hash,
                    self.username,
                    self.phone,
                    self.name,
                )

        class SentFile(base):
            query = qp
            __tablename__ = f"{prefix}sent_files"
            __table_args__ = {"extend_existing": True}

            session_id = Column(String(20), primary_key=True)
            md5_digest = Column(LargeBinary, primary_key=True)
            file_size = Column(Integer, primary_key=True)
            type = Column(Integer, primary_key=True)
            id = Column(BigInteger)
            hash = Column(BigInteger)

            def __str__(self):
                return "SentFile('{}', {}, {}, {}, {}, {})".format(
                    self.session_id,
                    self.md5_digest,
                    self.file_size,
                    self.type,
                    self.id,
                    self.hash,
                )

        class UpdateState(base):
            query = qp
            __tablename__ = f"{prefix}update_state"
            __table_args__ = {"extend_existing": True}

            session_id = Column(String(20), primary_key=True)
            entity_id = Column(BigInteger, primary_key=True)
            pts = Column(BigInteger)
            qts = Column(BigInteger)
            date = Column(BigInteger)
            seq = Column(BigInteger)
            unread_count = Column(Integer)

        class Account(base):
            query = qp
            __tablename__ = f"{prefix}accounts"
            __table_args__ = {"extend_existing": True}

            session_id = Column(String(20), primary_key=True)
            api_id = Column(BigInteger, nullable=False)
            api_hash = Column(String(255), nullable=False)

            def __str__(self):
                return f"Account('{self.session_id}', {self.api_id}, '{self.api_hash}')"

            def to_dict(self):
                return {
                    "session_id": self.session_id,
                    "api_id": self.api_id,
                    "api_hash": self.api_hash,
                }

        return Version, Session, Entity, SentFile, UpdateState, Account

    def _add_column(self, table: Any, column: Column) -> None:
        column_name = column.compile(dialect=self.db_engine.dialect)
        column_type = column.type.compile(self.db_engine.dialect)
        self.db_engine.execute(
            f"ALTER TABLE {table.__tablename__} ADD COLUMN {column_name} {column_type}"
        )

    def check_and_upgrade_database(self) -> None:
        row = self.Version.query.all()
        version = row[0].version if row else 1
        if version == LATEST_VERSION:
            return

        self.Version.query.delete()

        if version == 1:
            self.UpdateState.__table__.create(self.db_engine)
            version = 3
        elif version == 2:
            self._add_column(
                self.UpdateState, Column(type=Integer, name="unread_count")
            )

        self.db.add(self.Version(version=version))
        self.db.commit()

    def new_session(self, session_id: str) -> "AlchemySession":
        return self.alchemy_session_class(self, session_id)

    def has_session(self, session_id: str) -> bool:
        if self.core_mode:
            query = select([func.count()]).where(
                and_(
                    self.Session.__table__.c.session_id == session_id,
                    self.Session.__table__.c.auth_key != b"",
                )
            )
            count = self.db_engine.execute(query).scalar()
        else:
            count = self.Session.query.filter(
                self.Session.session_id == session_id
            ).count()
        return count > 0

    def list_sessions(self) -> list:
        if self.core_mode:
            query = select([self.Session.__table__.c.session_id])
            result = self.db_engine.execute(query)
            return [row[0] for row in result]
        else:
            return [s.session_id for s in self.Session.query.all()]

    def save(self) -> None:
        if self.db:
            self.db.commit()

    def delete(self, session_id: str) -> None:
        """Удаляет все данные, связанные с указанным session_id, из всех таблиц."""
        try:
            if self.core_mode:
                # Режим без ORM - используем прямое выполнение SQL
                tables = [
                    self.Session,
                    self.Entity,
                    self.SentFile,
                    self.UpdateState,
                    self.Account,
                ]
                for table in tables:
                    stmt = table.__table__.delete().where(
                        table.__table__.c.session_id == session_id
                    )
                    self.db_engine.execute(stmt)
            else:
                self.db.query(self.Session).filter(
                    self.Session.session_id == session_id
                ).delete()

                # Удаляем из таблицы Entity
                self.db.query(self.Entity).filter(
                    self.Entity.session_id == session_id
                ).delete()

                # Удаляем из таблицы SentFile
                self.db.query(self.SentFile).filter(
                    self.SentFile.session_id == session_id
                ).delete()

                # Удаляем из таблицы UpdateState
                self.db.query(self.UpdateState).filter(
                    self.UpdateState.session_id == session_id
                ).delete()

                self.db.query(self.Account).filter(
                    self.Account.session_id == session_id
                ).delete()

                self.db.commit()

        except Exception:
            if not self.core_mode and self.db:
                self.db.rollback()
            raise

    def get_info_by_phone(self, phone: str) -> Optional[dict]:
        try:
            if self.core_mode:
                query = (
                    select(
                        [
                            self.Account.__table__.c.session_id,
                            self.Account.__table__.c.api_id,
                            self.Account.__table__.c.api_hash,
                        ]
                    )
                    .where(self.Account.__table__.c.session_id == phone)
                    .limit(1)
                )
                result = self.db_engine.execute(query).fetchone()

                if not result:
                    return None

                return {
                    "session_id": result[0],
                    "api_id": result[1],
                    "api_hash": result[2],
                }
            else:

                account = (
                    self.db.query(self.Account)
                    .filter(self.Account.session_id == phone)
                    .first()
                )

                if not account:
                    return None

                return {
                    "session_id": account.session_id,
                    "api_id": account.api_id,
                    "api_hash": account.api_hash,
                }

        except Exception as e:
            if not self.core_mode and self.db:
                self.db.rollback()
            raise ValueError(f"Ошибка при получении информации об аккаунте: {e}")

    def add_account(self, session_id: str, api_id: int, api_hash: str) -> None:
        """Adds a new account record to the database.

        Args:
            session_id: The session identifier (primary key)
            id: The account ID
            hash: The account hash
        """
        try:
            if self.core_mode:
                # For core mode (raw SQL)
                stmt = self.Account.__table__.insert().values(
                    session_id=session_id, api_id=api_id, api_hash=api_hash
                )
                self.db_engine.execute(stmt)
            else:
                # For ORM mode
                account = self.Account(
                    session_id=session_id, api_id=api_id, api_hash=api_hash
                )
                self.db.add(account)
                self.db.commit()
        except Exception as e:
            if not self.core_mode and self.db:
                self.db.rollback()
            raise ValueError(f"Error adding account: {e}")

    async def get_accounts(self) -> list[Dict[str, str | int]]:
        return [acc.to_dict() for acc in self.db.query(self.Account).all()]
