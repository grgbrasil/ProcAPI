# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.test import TestCase
from mixer.backend.mongoengine import Mixer
from mongoengine import *

from ..models import Processo


class TestProcesso(TestCase):

    def setUp(self):
        mixer = Mixer(commit=False)
        self.processo = mixer.blend(Processo, numero='12345')

    def test_a_is_none(self):
        self.assertEqual(self.processo.numero, '12345')
