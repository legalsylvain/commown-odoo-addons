{
    'name': 'Rental product',
    'category': 'Sale',
    'summary': 'Define products as rental products',
    'version': '10.0.4.0.0',
    'description': """Rental products have a fixed deposit and recurring price, displayed on the product page""",
    'author': "Commown SCIC SAS",
    'license': "AGPL-3",
    'website': "https://commown.fr",
    'depends': ['website_sale', 'document', 'base_action_rule',
                'contract_payment_auto', 'contract_payment_mode',
                'product_contract',
    ],
    'external_dependencies': {},
    'data': [
        'views/contract_view.xml',
        'views/payment_transaction.xml',
        'views/product_template.xml',
        'views/sale_order.xml',
        'views/website_sale_templates.xml',
        'views/website_portal_sale_templates.xml',
    ],
    'installable': True,
}
