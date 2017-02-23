# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

from __future__ import absolute_import

from .service import EpoService

__version__ = "0.1.2"


def get_version():
    """
    Returns the version of the McAfee ePolicy Orchestrator (ePO) service

    :return: The version of the McAfee ePolicy Orchestrator (ePO) service
    """
    return __version__

