# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of Launch Control.
#
# Launch Control is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# Launch Control is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Launch Control.  If not, see <http://www.gnu.org/licenses/>.

"""
Unit tests of the TestClient support class
"""
from django.contrib.auth.models import User
from django.test import TestCase

from dashboard_app.tests.utils import TestClient


class TestClientTest(TestCase):

    _USER = "user"

    urls = 'dashboard_app.tests.urls'

    def setUp(self):
        super(TestClientTest, self).setUp()
        self.client = TestClient()
        self.user = User(username=self._USER)
        self.user.save()

    def test_auth(self):
        self.client.login_user(self.user)
        response = self.client.get("/auth-test/")
        self.assertEqual(response.content, self._USER)

    def test_no_auth(self):
        response = self.client.get("/auth-test/")
        self.assertEqual(response.content, '')

