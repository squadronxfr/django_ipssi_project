# -*- coding: utf-8 -*-
# Ce fichier permet à la découverte de tests basée sur BASE_DIR de trouver nos tests
# situés dans l'app accounts (qui est hors de BASE_DIR).
from accounts.tests.test_basic import *  # noqa: F401,F403
