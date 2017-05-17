#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from agent.agent.util import fields, Field, And, Or
from agent.agent.agent import Agent
from agent.agent import source, output, sender
from agent.config import rule, ruletocfg, rulebase

try:
    from blaze_agent import register
    register(uri='agent:.+', priority=12)
except ImportError:
    pass

__author__ = 'tong'
