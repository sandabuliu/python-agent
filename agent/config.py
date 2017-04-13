#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import ConfigParser

__author__ = 'tong'

if hasattr(sys, 'frozen'):
    try:
        if hasattr(sys, 'frozen') and isinstance(sys.executable, str):
            sys.executable = sys.executable.decode(sys.getfilesystemencoding())
    except:
        pass

    dirname = os.path.dirname(sys.executable)
    if 'library.zip' in os.listdir(dirname):
        ROOT_PATH = os.path.abspath(os.path.join(dirname, '..', '..'))
    else:
        ROOT_PATH = os.path.abspath(dirname)
    if 'appdata' not in os.listdir(ROOT_PATH):
        raise Exception('ERROR ROOT PATH: %s' % ROOT_PATH)
else:
    ROOT_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

PATH = {
    'ROOT': ROOT_PATH,
    'RULE': [os.path.join(ROOT_PATH, 'rule')]
}


def config(filename):
    if not os.path.exists(filename):
        raise Exception('No such config file %s' % filename)
    cfg = ConfigParser.ConfigParser()
    cfg.read(filename)
    return cfg


class Rulebase(object):
    @staticmethod
    def append(filename):
        PATH['RULE'].append(filename)

    @staticmethod
    def remove(index):
        PATH['RULE'].pop(index)

    @staticmethod
    def all():
        return PATH['RULE']


def rule(name='root', rulebase=None):
    def _decode_list(data):
        rv = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = _decode_list(item)
            elif isinstance(item, dict):
                item = _decode_dict(item)
            rv.append(item)
        return rv

    def _decode_dict(data):
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            elif isinstance(value, list):
                value = _decode_list(value)
            elif isinstance(value, dict):
                value = _decode_dict(value)
            rv[key] = value
        return rv

    bools = {'1': True, 'yes': True, 'true': True, 'on': True,
             '0': False, 'no': False, 'false': False, 'off': False}

    def rule_type(rl):
        from logparser import Rule
        r = Rule()
        r.type = rl['type']
        value = rl.get('rule')
        if r.ruleparser.TYPE is dict:
            value = json.loads(value, object_hook=_decode_dict)
        if r.ruleparser.TYPE is bool:
            value = bools.get(value.lower(), False)
        return value

    for rulebase in ([rulebase] if rulebase else PATH['RULE']):
        try:
            rules = dict(config(rulebase).items(name))
            break
        except:
            pass
    else:
        raise Exception('No such rule %s' % name)

    ret = {'type': rules['type'], 'rule': rule_type(rules)}
    if rules.get('fields'):
        try:
            fields = json.loads(rules['fields'], object_hook=_decode_dict)
        except:
            fields = [i.strip() for i in rules['fields'].split(',')]
        if isinstance(fields, list):
            fields = dict(zip(fields, [str(i) for i in range(len(fields))]))
        fields.pop(None, None)
        fields.pop('', None)
        ret['fields'] = fields
    if rules.get('subrules'):
        ret['subrules'] = {k: rule(v, rulebase) for k, v in
                           json.loads(rules['subrules'], object_hook=_decode_dict).items()}
    return ret


def ruletocfg(name, rule):
    for key in ('type', 'rule'):
        if key not in rule:
            raise Exception('rule need %s' % key)

    rules = []
    items = [
        '[%s]' % name,
        'type=%s' % rule['type'],
        'rule=%s' % (json.dumps(rule['rule']) if isinstance(rule['rule'], dict) else rule['rule'])
    ]
    if 'fields' in rule:
        items.append('fields=%s' % json.dumps(rule['fields']))
    if 'subrules' in rule:
        subrules = {key: '%s_%s' % (name, key) for key, value in rule['subrules'].items()}
        items.append('subrules=%s' % json.dumps(subrules))
        rules = [ruletocfg('%s_%s' % (name, key), value) for key, value in rule['subrules'].items()]

    ret = '\n'.join(items)
    rules.insert(0, ret)
    return '\n\n'.join(rules)

rulebase = Rulebase()
