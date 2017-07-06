# This file is part account_invoice_weight module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import configuration
from . import invoice

def register():
    Pool.register(
        configuration.Configuration,
        invoice.Invoice,
        module='account_invoice_weight', type_='model')
