from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestShareholderRegisterTC(TransactionCase):
    "Common class for the tests of this module"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        if not cls.env.company.chart_template_id:  # pragma: no cover
            # Load a CoA if there's none in current company
            coa = cls.env.ref("l10n_generic_coa.configurable_chart_template", False)
            if not coa:  # pragma: no cover
                # Load the first available CoA
                coa = cls.env["account.chart.template"].search(
                    [("visible", "=", True)], limit=1
                )
            coa.try_loading(company=cls.env.company, install_demo=False)

        cls.partner_1 = cls.env["res.partner"].create({"name": "Partner 1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Partner 2"})
        cls.partner_3 = cls.env["res.partner"].create({"name": "Partner 3"})

        cls.account_porteur = cls.env.ref(
            "commown_shareholder_register.account_porteur"
        )
        cls.account_soutien = cls.env.ref(
            "commown_shareholder_register.account_soutien"
        )
        cls.account_beneficiaire = cls.env.ref(
            "commown_shareholder_register.account_beneficiaire"
        )
        cls.account_balancing = cls.env.ref(
            "commown_shareholder_register.account_balancing"
        )

        cls.college_A = cls.env.ref("commown_shareholder_register.college_A")
        cls.college_B = cls.env.ref("commown_shareholder_register.college_B")
        cls.college_D = cls.env.ref("commown_shareholder_register.college_D")

        cls.cat_porteur = cls.env.ref("commown_shareholder_register.cat_porteur")
        cls.cat_soutien = cls.env.ref("commown_shareholder_register.cat_soutien")
        cls.cat_beneficiaire = cls.env.ref(
            "commown_shareholder_register.cat_beneficiaire"
        )

    @classmethod
    def _add_shares(cls, partner, account, date_tuple, amount):
        journal = (
            cls.env["account.journal"]
            .search(
                [("type", "=", "general"), ("company_id", "=", account.company_id.id)],
                limit=1,
            )
            .ensure_one()
        )
        move = cls.env["account.move"].create(
            {
                "name": "Test Account Move",
                "journal_id": journal.id,
                "date": date(*date_tuple),
            }
        )
        if amount < 0:
            attr2, attr1 = "credit", "debit"
        else:
            attr1, attr2 = "credit", "debit"

        cls.account_move_lines |= cls.env["account.move.line"].create(
            [
                {
                    "move_id": move.id,
                    "account_id": account.id,
                    "partner_id": partner.id,
                    "date": date(*date_tuple),
                    attr1: abs(amount),
                },
                {
                    "move_id": move.id,
                    "account_id": cls.account_balancing.id,
                    "partner_id": partner.id,
                    "date": date(*date_tuple),
                    attr2: abs(amount),
                },
            ]
        )
