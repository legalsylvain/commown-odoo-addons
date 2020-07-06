{
    'name': 'Commown SCIC SAS',
    'category': 'Business',
    'summary': 'Commown SCIC SAS business application',
    'version': '10.0.1.14.0',
    'description': "Commown SCIC SAS business application",
    'author': "Commown SCIC SAS",
    'license': "AGPL-3",
    'website': "https://commown.coop",
    'depends': [
        # Commown modules
        'account_asset_fiscal_year',
        'account_loan',
        'account_bank_statement_import_credit_coop',
        'account_bank_statement_import_lanef',
        'account_invoice_merge_auto_pay',
        'account_move_slimpay_import',
        'commown_shipping',
        'commown_lead_risk_analysis',
        'contract_auto_merge_invoice',
        'payment_slimpay',
        'payment_slimpay_issue',
        'product_rental',
        'rating_project_issue_nps',
        'sale_product_email',
        'urban_mine',
        'custom_report',
        'website_sale_affiliate_portal',
        'website_sale_affiliate_product_restriction',
        'website_sale_b2b',
        'website_sale_coupon',
        # OCA modules
        'account_payment_sale',
        'account_mass_reconcile',
        'account_move_stripe_import',
        'auth_signup',
        'base_action_rule',
        'crm',
        'mass_mailing',
        'mass_mailing_partner',
        'project_issue',
        'website_project_issue',
        'website_sale_cart_selectable',
        'website_sale_default_country',
        'website_sale_hide_price',
        'website_sale_require_login',
    ],

    'external_dependencies': {
        'python': ['magic'],
        'bin': ['rsvg-convert'],
    },

    'data': [
        'views/account_analytic_account.xml',
        'views/account_analytic_contract.xml',
        'views/address_template.xml',
        'views/auth_signup.xml',
        'views/cart.xml',
        'views/actions_sale_order.xml',
        'views/actions_account_invoice.xml',
        'views/product_template.xml',
        'views/project_issue.xml',
        'views/webclient_templates.xml',
        'views/website_portal_templates.xml',
        'views/website_sale_templates.xml',
        'views/website_site_portal_sale_templates.xml',
        'views/res_partner.xml',
        'views/crm_lead.xml',
        'data/product.xml',
        'data/mail_templates.xml',
        'data/project_project.xml',
    ],
    'qweb': [
        'static/src/xml/account_reconciliation.xml',
    ],
    'installable': True,
    'application': True,
}
