# This file is part account_invoice_weight module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pyson import Eval, Id
from trytond.pool import Pool, PoolMeta

__all__ = ['Invoice']


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'
    weight_uom = fields.Many2One('product.uom', 'Weight Uom',
        domain=[('category', '=', Id('product', 'uom_cat_weight'))],
        states={
            'readonly': Eval('state') != 'draft',
        }, depends=['state'])
    weight_digits = fields.Function(fields.Integer('Weight Digits'),
        'on_change_with_weight_digits')
    weight = fields.Float('Weight', digits=(16, Eval('weight_digits', 2)),
        states={
            'readonly': Eval('state') != 'draft',
        }, depends=['state', 'weight_digits'])
    weight_lines = fields.Function(fields.Float('Weight of Moves',
            digits=(16, Eval('weight_digits', 2)),
            depends=['weight_digits']), 'get_weight_lines')
    weight_func = fields.Function(fields.Float('Weight',
            digits=(16, Eval('weight_digits', 2)),
            depends=['weight_digits']), 'on_change_with_weight_func')

    @classmethod
    def get_weight_lines(cls, invoices, names):
        pool = Pool()
        Config = pool.get('account.configuration')
        Uom = pool.get('product.uom')

        config = Config(1)
        if config.weight_uom:
            default_uom = config.weight_uom
        else:
            default_uom, = Uom.search([('symbol', '=', 'g')], limit=1)

        weight = {}
        for invoice in invoices:
            weight[invoice.id] = 0.0
            to_uom = invoice.weight_uom or default_uom
            for line in invoice.lines:
                if line.quantity and line.product and line.product.weight:
                    from_uom = line.product.weight_uom
                    weight[invoice.id] += Uom.compute_qty(from_uom,
                        line.product.weight * line.quantity, to_uom,
                        round=False)

        return {'weight_lines': weight}

    @fields.depends('weight', 'weight_lines')
    def on_change_with_weight_func(self, name=None):
        if self.weight:
            return self.weight
        return self.weight_lines

    @fields.depends('weight_uom')
    def on_change_with_weight_digits(self, name=None):
        if self.weight_uom:
            return self.weight_uom.digits
        return 2
