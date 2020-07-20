import pytest
from aiosmtpd.controller import Controller
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.app import app, get_db
from app.database import Base


@pytest.fixture()
def client():
    database_url = "sqlite:///./test.db"

    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        yield client
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def email_catcher():
    class TestHandler:
        received_mail = []

        async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
            if not address.endswith("@example.com"):
                return "550 not relaying to that domain"
            envelope.rcpt_tos.append(address)
            return "250 OK"

        async def handle_DATA(self, server, session, envelope):
            self.received_mail.append(envelope)
            return "250 Message accepted for delivery"

    controller = Controller(TestHandler(), hostname="localhost", port=8025)
    controller.start()
    try:
        yield controller
    finally:
        controller.stop()
