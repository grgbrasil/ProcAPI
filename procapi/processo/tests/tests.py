from django.test import TestCase

import mongoengine
from mongoengine import connect
from mongoengine.connection import (
    get_connection
)

from ..models import Processo


class TestA(TestCase):

    def setUp(self):
        import mongomock

        # me = connect(
        #     # db='mongoenginetest',
        #     host='mongomock://localhost/mongoenginetest',
        #     alias='testdb',
        # )
        # print(me.get_default_database())
        # self.me.get_connection()

        self.c1 = connect(host='mongomock://localhost/asdfasdf')

        import random
        for p in enumerate(range(10)):
            randomico = random.random()
            self.proc = Processo.objects.create(
                numero='N.{}'.format(randomico),
                chave='Chave {}'.format(randomico),
            )
            print(self.proc.to_json())

        self.a = None

    # def tearDown(self):
    #     mongoengine.connection._connection_settings = {}
    #     mongoengine.connection._connections = {}
    #     mongoengine.connection._dbs = {}

    def test_a_is_none(self):
        # print(self.conn)
        self.assertIsNone(self.a)
