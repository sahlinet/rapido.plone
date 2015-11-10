# -*- coding: utf-8 -*-
import json
from plone.app.theming.interfaces import IThemeSettings
from plone.app.theming.utils import applyTheme
from plone.app.theming.utils import getTheme
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from zope.component import getUtility
import Globals
import unittest2 as unittest

from rapido.plone.testing import RAPIDO_PLONE_FUNCTIONAL_TESTING


class TestCase(unittest.TestCase):

    layer = RAPIDO_PLONE_FUNCTIONAL_TESTING

    def setUp(self):
        # Enable debug mode always to ensure cache is disabled by default
        Globals.DevelopmentMode = True

        self.settings = getUtility(IRegistry).forInterface(IThemeSettings)
        self.settings.enabled = True
        theme = getTheme('rapido.plone.tests')
        applyTheme(theme)

        import transaction
        transaction.commit()

        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.raiseHttpErrors = False
        self.browser.addHeader('Accept', 'application/json')

    def tearDown(self):
        Globals.DevelopmentMode = False

    def test_json_refresh_no_token(self):
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )
        self.browser.post(
            self.portal.absolute_url() + '/@@rapido/testdb/refresh', '')
        self.assertEquals(self.browser.headers["status"],
            '500 Internal Server Error')
        self.assertEquals(self.browser.contents,
            '{"error": "Form authenticator is invalid."}')

    def test_json_refresh(self):
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )
        self.browser.open(
            self.portal.absolute_url() + '/@@rapido/testdb')
        self.assertTrue('x-csrf-token' in self.browser.headers)
        token = self.browser.headers['x-csrf-token']
        self.browser.addHeader('x-csrf-token', token)
        self.browser.post(
            self.portal.absolute_url() + '/@@rapido/testdb/refresh', '')
        self.assertEquals(self.browser.headers["status"],
            '200 Ok')
        self.assertEquals(self.browser.contents,
            '{"success": "refresh", "indexes": ["id"]}')
