import pytest
from aiosmtpd.controller import Controller
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.app import app, get_db
from app.database import Base


@pytest.fixture()
def client():
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
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


def sign_person_up(client, name, email=None, description=None):
    obj = {"name": name}
    if email:
        obj["email"] = email
    if description:
        obj["description"] = description
    return client.post("/person/", headers={"X-Token": "coneofsilence"}, json=obj)


def edit_person(client, _id, new_description):
    obj = get_person(client, _id).json()
    obj["description"] = new_description
    return client.put("/person/", headers={"X-Token": "coneofsilence"}, json=obj)


def get_person(client, _id):
    return client.get("/person/{}".format(_id), headers={"X-Token": "coneofsilence"})


def was_person_emailed(client, _id):
    response = get_person(client, _id)
    assert response.status_code == 200
    return response.json()["signup_email_success"]


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


def validate_email(envelope, expected_email, expected_name):
    # Server sends an alert to that email address, with the person’s name in the subject line.
    assert len(envelope.rcpt_tos) == 1
    assert envelope.rcpt_tos[0] == expected_email

    assert "Subject: {}".format(expected_name) in envelope.content.decode(
        "utf8", errors="replace"
    )


def test_add_new_person_correctly_succeeds(client, email_catcher):
    """
    GIVEN
    Zak hasn't sign up yet

    WHEN
    He signs up

    THEN
    The signup works
    An email with the correct format shows up
    His information is added to the database
    """
    email = "zak@example.com"
    name = "Zak"
    response = sign_person_up(
        client=client, name=name, email=email, description="Without a C"
    )
    assert response.status_code == 200
    actual_data = response.json()
    assert "id" in actual_data
    mail = email_catcher.handler.received_mail
    assert len(mail) == 1
    validate_email(mail[0], expected_email=email, expected_name=name)
    assert was_person_emailed(client, _id=response.json()["id"]) == True


def test_add_existing_person_fails(client, email_catcher):
    """
    GIVEN
    Zak has signed up

    WHEN
    He signs up

    THEN
    It fails because he's already signed up
    """
    email = "zak@example.com"
    name = "Zak"
    response = sign_person_up(
        client=client, name=name, email=email, description="Without a C"
    )
    assert response.status_code == 200
    response = sign_person_up(
        client=client, name=name, email=email, description="Without a C"
    )
    assert response.status_code == 400


def test_add_new_person_without_email_fails(client):
    """
    WHEN
    Zak tries to sign up without providing an email

    THEN
    He sees a failure because you have to have an email
    """
    email = None
    name = "Zak"
    response = sign_person_up(
        client=client, name=name, email=email, description="Without a C"
    )
    assert response.status_code == 422


def test_bad_email(client):
    """
    WHEN
    Zak tries to sign up with a bad email address

    THEN
    He sees a failure
    """
    email = "nope"
    name = "Zak"
    response = sign_person_up(
        client=client, name=name, email=email, description="Without a C"
    )
    assert response.status_code == 422


def test_edit_persons_description(client, email_catcher):
    email = "zak@example.com"
    name = "Zak"
    new_description = "Rethinking the C"
    response = sign_person_up(
        client=client, name=name, email=email, description="Without a C"
    )
    _id = response.json()["id"]
    assert response.status_code == 200
    response = edit_person(client, _id, new_description)
    assert response.status_code == 200
    response = get_person(client, _id)
    assert response.status_code == 200
    assert response.json()["description"] == new_description


def test_edit_person_who_isnt_there_fails(client, email_catcher):
    email = "zak@example.com"
    name = "Zak"
    response = sign_person_up(
        client=client, name=name, email=email, description="Without a C"
    )
    assert response.status_code == 200
    zak = response.json()
    zak["id"] = "999"
    response = client.put("/person/", headers={"X-Token": "coneofsilence"}, json=zak)
    assert response.status_code == 404


def test_get_failure(client):
    response = get_person(client, 999)
    assert response.status_code == 404
