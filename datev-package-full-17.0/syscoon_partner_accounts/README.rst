=========================
syscoon Finance Interface
=========================

Installation
============

To install this module, you need to:

#. Go to apps and search for syscoon_partner_accounts and install it

Description
===========

* If you have used partner / supplier numbers in the past, you need to install
  * syscoon_partner_customer_supplier_number
* There will be more modules that extend this module
  * syscoon_partner_accounts_automatic
  * syscoon_partner_accounts_automaitc_invoice
  * syscoon_partner_accounts_automaitc_sale
  * syscoon_partner_accounts_automaitc_purchase

Changelog
=========

* 17.0.0.0.4
  * fix account.account not generated if selected in configuration

* 17.0.0.0.3
  * change getting sequence for partner numbers to get_by_id

* 17.0.0.0.2
  * improve translation de_DE

* 17.0.0.0.1
  * Initial version
  * ported from 16.0.0.0.8
  * removed partner numbers (supplier / customer because of the new module
    syscoon_partner_customer_supplier_number)

Credits
=======

.. |copy| unicode:: U+000A9 .. COPYRIGHT SIGN
.. |tm| unicode:: U+2122 .. TRADEMARK SIGN

- `Mathias Neef <mathias.neef@syscoon.com>`__ |copy|
  `syscoon <http://www.syscoon.com>`__ |tm| 2024
- `Ebin PG <ebin.pg@syscoon.com>`** |copy| 
  `syscoon <http://www.syscoon.com>`** |tm| 2024
