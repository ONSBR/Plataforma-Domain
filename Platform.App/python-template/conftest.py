import time
import json

import pytest
import docker
from sqlalchemy import create_engine, orm
from sqlalchemy_utils import database_exists, create_database, drop_database

from core.temporal.session import sessionmaker

from database import Base
from app import create_app


class SETTINGS:
    DB_HOST = "127.0.0.1"
    DB_PORT = 5432
    DB_NAME = "test_domain"
    DB_USER = "test_user"
    DB_PASSWORD = "passwd"
    KEEP_DB = False

def load_db_container():
    container_name = 'postgres_domain_test_db'
    client = docker.from_env()
    containers = client.containers.list(filters={'name': container_name})

    if containers:
        return containers[0]

    container = client.containers.run(
        'postgres',
        name=container_name,
        auto_remove=True,
        detach=True,
        ports={'5432/tcp': '5432'},
        environment=[f'POSTGRES_USER={SETTINGS.DB_USER}', f'POSTGRES_PASSWORD={SETTINGS.DB_PASSWORD}'],
    )

    # waiting for the container to be up and set.
    time.sleep(3)
    return container

@pytest.fixture(scope='session')
def engine(request):
    """Creates a new database connection for each test section.
    """
    container = load_db_container()


    engine = create_engine(
        f'postgresql+psycopg2://{SETTINGS.DB_USER}:{SETTINGS.DB_PASSWORD}@{SETTINGS.DB_HOST}:{SETTINGS.DB_PORT}/{SETTINGS.DB_NAME}',
        echo=False)

    if not database_exists(engine.url):
        create_database(engine.url)

    def teardown():
        if not SETTINGS.KEEP_DB:
            container.stop()

    request.addfinalizer(teardown)
    return engine


@pytest.fixture(scope='session', autouse=True)
def db(request, engine):
    _db = Base.metadata
    _db.create_all(engine)
    return _db


def test_session_factory(connection, transaction):
    """Creates a new temporal session for a test."""
    session_factory = sessionmaker(bind=connection)
    session = orm.scoped_session(session_factory)
    return session


@pytest.fixture(scope='session')
def connection(request, engine):
    c = engine.connect()

    def teardown():
        c.close()

    request.addfinalizer(teardown)
    return c


@pytest.fixture(scope="function")
def transaction(request, connection):
    t = connection.begin()

    def teardown():
        t.rollback()

    request.addfinalizer(teardown)
    return t


@pytest.fixture(scope="function")
def app(connection, transaction):
    application = create_app()
    application.debug = True
    application.testing = True
    application.session_factory = lambda: test_session_factory(connection, transaction)
    return application


@pytest.fixture(scope='function')
def session(request, connection, app):
    session = app.session_factory()

    def teardown():
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope="function")
def test_client(request, app):
    client = app.test_client()

    def get_json(uri):
        response = client.get(uri, follow_redirects=True)
        return (response.status_code, json.loads(response.data), )

    setattr(client, 'get_json', get_json)
    return client
