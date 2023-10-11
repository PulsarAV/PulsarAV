import datetime
import logging
from itertools import chain, islice
from operator import itemgetter

from odoo import SUPERUSER_ID
from odoo.api import Environment

_logger = logging.getLogger(__name__)
COMPUTED_FIELDS = {"account.move": ["commercial_partner_id"]}


def migrate(cr, version):
    _logger.info('post_init: Start')

    # Call compute methods
    for modelname, model_data in COMPUTED_FIELDS.items():
        recompute_fields(cr, modelname, model_data, _logger)

    _logger.info('post_init: End')


def env(cr):
    return Environment(cr, SUPERUSER_ID, {})


def recompute_fields(cr, model, fields, logger, ids=None, chunk_size=256):
    if ids is None:
        cr.execute('SELECT id FROM "%s"' % model.replace('.', '_'))
        ids = tuple(map(itemgetter(0), cr.fetchall()))

    model_obj = env(cr)[model]
    size = (len(ids) + chunk_size - 1) / chunk_size
    qual = '%s %d-bucket' % (model, chunk_size) if chunk_size != 1 else model
    for subids in log_progress(
        chunks(ids, chunk_size, list), logger, qualifier=qual, size=size
    ):
        model_obj.browse(subids)
        for field in fields:
            env(cr).add_to_compute(model_obj._fields[field], model_obj.search([]))


def log_progress(iter_var, logger, qualifier="elements", size=None):
    if size is None:
        size = len(iter_var)
    size = float(size)
    time_now_0 = time_now_1 = datetime.datetime.now()
    for i, e in enumerate(iter_var, 1):
        yield e
        t2 = datetime.datetime.now()
        if (t2 - time_now_1).total_seconds() > 60:
            time_now_1 = datetime.datetime.now()
            tdiff = t2 - time_now_0
            logger.info(
                "[%.02f%%] %d/%d %s processed in %s (TOTAL estimated time: %s)",
                (i / size * 100.0),
                i,
                size,
                qualifier,
                tdiff,
                datetime.timedelta(seconds=tdiff.total_seconds() * size / i),
            )


def chunks(iterable, size, fmt=None):
    if fmt is None:
        fmt = {str: "".join}.get(type(iterable), iter)

    it = iter(iterable)
    try:
        while True:
            yield fmt(chain((next(it),), islice(it, size - 1)))
    except StopIteration:
        return
