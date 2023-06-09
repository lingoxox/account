#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = "SYK"
__date__ = "2023/4/18 下午1:20"

from oslo_config import cfg

SERVER_NAME = 'account'
DEFAULT_LOCAL_AMQP_SERVER_ADDRESS = 'amqp://guest:guest@localhost:5672'

FILE_OPTIONS = {

    'database': [
        cfg.StrOpt('connection',
                   default=f'mysql+pymysql://root:stack@127.0.0.1/{SERVER_NAME}',
                   help=''),
        cfg.StrOpt('slave_connection',
                   default='',
                   help=''),
        cfg.StrOpt('migrate_version_dir',
                   default='/usr/local/lib/python3.9/site-packages/'),
    ],
    'cache': [
        cfg.StrOpt('connection',
                   default='url:redis://127.0.0.1:6379/0',
                   help=''),
        cfg.IntOpt('default_timeout',
                   default=300,
                   help='cache default timeout'),
        cfg.StrOpt('cache_key_prefix',
                   default=f'{SERVER_NAME}',
                   help='cached key prefix'),
    ],

    'AMQP_CONFIGS': [

        cfg.DictOpt('default',
                    default={
                        'AMQP_SERVER_ADDRESS': DEFAULT_LOCAL_AMQP_SERVER_ADDRESS,
                        'EXCHANGE_NAME': None,
                        'EXCHANGE_TYPE': 'topic',
                        'QUEUE_NAME': None,
                        'ROUTING_KEY': None
                    }),

        cfg.DictOpt('eventbus',
                    default={
                        'AMQP_SERVER_ADDRESS': DEFAULT_LOCAL_AMQP_SERVER_ADDRESS,
                        'EXCHANGE_TYPE': 'fanout',
                    }),

        cfg.StrOpt('AMQP_SERVER_ADDRESS',
                   default=DEFAULT_LOCAL_AMQP_SERVER_ADDRESS,
                   help=''),

        cfg.StrOpt('EXCHANGE_NAME',
                   default=f'{SERVER_NAME}.ms.events',
                   help=''),

        cfg.StrOpt('QUEUE_NAME',
                   default=f'{SERVER_NAME}.events',
                   help=''),

        cfg.StrOpt('ROUTING_KEY',
                   default="{}.routing",
                   help=''),

    ],

    'celery': [
        cfg.StrOpt('broker',
                   default='redis://127.0.0.1:6379/1',
                   help=''),
    ],

    'http_service': [
        cfg.ListOpt('plugins',
                    default=[
                        'example',
                    ],
                    help='List of Business Plugin'
                    ),
    ],

    'service': [

        cfg.BoolOpt('debug',
                    default=False,
                    help="service debug Mode"),

        cfg.StrOpt(f'api_{SERVER_NAME}_listen',
                   default="0.0.0.0",
                   help='IP address on which openlab trit API listens'),

        cfg.IntOpt(f'api_{SERVER_NAME}_listen_port',
                   default=16091,
                   min=1, max=65535,
                   help='Port on which openlab trit API listens'),

        cfg.IntOpt(f'api_{SERVER_NAME}_workers',
                   default=1,
                   help='Number of separate API worker processes for '
                        'service. If not specified or 0, the default is '
                        'equal to the number of CPUs available for '
                        'best performance.'),

        cfg.IntOpt(f'{SERVER_NAME}_sync_workers',
                   default=1,
                   help='Number of separate SYNC worker processes for '
                        'service. If not specified or 0, the default is '
                        'equal to the number of CPUs available for '
                        'best performance.'),

    ]

}
