from sqlalchemy import BigInteger, Column, Integer, LargeBinary, String

from .base import Base


class Version(Base):
    __tablename__ = "version"

    version = Column(Integer, primary_key=True)

    def __str__(self):
        return f"Version('{self.version}')"


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String(255), primary_key=True)
    dc_id = Column(Integer, primary_key=True)
    server_address = Column(String(255))
    port = Column(Integer)
    auth_key = Column(LargeBinary)

    def __str__(self):
        return f"Session('{self.session_id}', {self.dc_id}, \
            '{self.server_address}', {self.port}, {self.auth_key})"


class Entity(Base):
    __tablename__ = "entities"

    session_id = Column(String(255), primary_key=True)
    id = Column(BigInteger, primary_key=True)
    hash = Column(BigInteger, nullable=False)
    username = Column(String(32))
    phone = Column(BigInteger)
    name = Column(String(255))

    def __str__(self):
        return f"Entity('{self.session_id}', {self.id}, {self.hash}, \
            '{self.username}', '{self.phone}', '{self.name}')"


class SentFile(Base):
    __tablename__ = "sent_files"

    session_id = Column(String(255), primary_key=True)
    md5_digest = Column(LargeBinary, primary_key=True)
    file_size = Column(Integer, primary_key=True)
    type = Column(Integer, primary_key=True)
    id = Column(BigInteger)
    hash = Column(BigInteger)

    def __str__(self):
        return f"SentFile('{self.session_id}', {self.md5_digest},\
            {self.file_size}, {self.type}, {self.id}, {self.hash})"


class UpdateState(Base):
    __tablename__ = "update_state"

    session_id = Column(String(255), primary_key=True)
    entity_id = Column(BigInteger, primary_key=True)
    pts = Column(BigInteger)
    qts = Column(BigInteger)
    date = Column(BigInteger)
    seq = Column(BigInteger)
    unread_count = Column(Integer)

    def __str__(self):
        return f"UpdateState('{self.session_id}', {self.entity_id}, {self.pts}, \
            {self.qts}, {self.date}, {self.seq}, {self.unread_count})"


class Account(Base):
    __tablename__ = "accounts"

    session_id = Column(String(255), primary_key=True)
    api_id = Column(BigInteger, nullable=False)
    api_hash = Column(String(255), nullable=False)
