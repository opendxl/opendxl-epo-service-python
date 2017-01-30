# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

import logging

# Configure local logger
logger = logging.getLogger(__name__)

class EpoService(object):

    def __init__(self, dxl_client):
        """
        Constructor parameters:

        :param dxl_client: The DXL client to use for communication with the DXL fabri
        """
        self.__dxl_client = dxl_client

