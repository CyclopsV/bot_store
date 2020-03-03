edit_admin = 'ed'
get_product = 'gp'

edit = ['en',  # edit_name
        'el',  # edit_location
        'ep',  # edit_phone
        ]

order = ['lo',  # list_orders
         'no',  # new_order
         'go',  # get_order
         ]

prod = ['ap',  # add 0
        'dp',  # delete 1
        [  # edit 2
            'pen',  # name 0
            'pei',  # img 1
            'ped',  # definition 2
            'pep',  # price 3
            'pea'  # available 4
        ],
        [  # filter 3
            'pfl',  # <5000 0
            'pft',  # 5000< 1
            'aap'  # add 2
        ]]
