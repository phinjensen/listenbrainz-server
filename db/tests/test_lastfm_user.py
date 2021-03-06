from __future__ import absolute_import, print_function, unicode_literals
from db.testing import DatabaseTestCase
import logging
from datetime import datetime
from tests.utils import generate_data
from webserver.influx_connection import init_influx_connection
import db
from db.lastfm_user import User
from sqlalchemy import text
import config


class TestAPICompatUserClass(DatabaseTestCase):

    def setUp(self):
        super(TestAPICompatUserClass, self).setUp()
        self.log = logging.getLogger(__name__)
        self.logstore = init_influx_connection({
            'INFLUX_HOST': config.INFLUX_HOST,
            'INFLUX_PORT': config.INFLUX_PORT,
            'INFLUX_DB_NAME': config.INFLUX_DB_NAME,
            'REDIS_HOST': config.REDIS_HOST,
            'REDIS_PORT': config.REDIS_PORT,
        })

        # Create a user
        uid = db.user.create("test")
        self.assertIsNotNone(db.user.get(uid))
        with db.engine.connect() as connection:
            result = connection.execute(text("""
                SELECT *
                  FROM "user"
                 WHERE id = :id
            """),{
                "id": uid,
            })
            row = result.fetchone()
            self.user = User(row['id'], row['created'], row['musicbrainz_id'], row['auth_token'])

        # Insert some listens
        date = datetime(2015, 9, 3, 0, 0, 0)
        self.log.info("Inserting test data...")
        test_data = generate_data(date, 100)
        self.logstore.insert(test_data)
        self.log.info("Test data inserted")

    def tearDown(self):
        super(TestAPICompatUserClass, self).tearDown()

    def test_user_get_id(self):
        uid = User.get_id(self.user.name)
        self.assertEqual(uid, self.user.id)

    def test_user_load_by_name(self):
        user = User.load_by_name(self.user.name)
        assert isinstance(user, User) == True
        self.assertDictEqual(user.__dict__, self.user.__dict__)

    def test_user_load_by_id(self):
        user = User.load_by_id(self.user.id)
        assert isinstance(user, User) == True
        self.assertDictEqual(user.__dict__, self.user.__dict__)
