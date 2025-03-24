# Copyright 2015-17 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, TransactionCase


class TestSaleOrderLineVariantDescription(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fiscal_position_model = cls.env["account.fiscal.position"]
        cls.tax_model = cls.env["account.tax"]
        cls.pricelist_model = cls.env["product.pricelist"]
        cls.uom_uom_model = cls.env["uom.uom"]
        cls.product_tmpl_model = cls.env["product.template"]
        cls.product_model = cls.env["product.product"]
        cls.so_model = cls.env["sale.order"]
        cls.so_line_model = cls.env["sale.order.line"]
        cls.partner = cls.env.ref("base.res_partner_1")

    def test_product_id_change(self):
        uom = self.uom_uom_model.search([("name", "=", "Units")])[0]

        tax_form = Form(self.tax_model)
        tax_form.name = "Include tax"
        tax_form.amount = 0.21
        tax_include = tax_form.save()

        product_tmpl_form = Form(self.product_tmpl_model)
        product_tmpl_form.name = "Product template"
        product_tmpl_form.list_price = 121
        product_tmpl_form.taxes_id.add(tax_include)
        product_tmpl = product_tmpl_form.save()

        product = product_tmpl.product_variant_id
        product.write(
            {
                "variant_description_sale": "Product variant description",
            }
        )

        fp_form = Form(self.fiscal_position_model)
        fp_form.name = "fiscal position"
        fp = fp_form.save()

        so_form = Form(self.so_model)
        so_form.partner_id = self.partner
        so_form.fiscal_position_id = fp
        so = so_form.save()

        with Form(so) as so_form, so_form.order_line.new() as line_form:
            line_form.product_id = product
            line_form.product_uom_qty = 1.0
            line_form.product_uom = uom
            line_form.price_unit = 121.0

        so_line = so.order_line[0]

        self.assertEqual(product.variant_description_sale, so_line.name)
