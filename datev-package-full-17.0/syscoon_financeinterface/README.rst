=========================
syscoon Finance Interface
=========================

Installation
============

To install this module, you need to:

Go to apps and search for syscoon_financeinterface

Description
===========

* Baic module for the finance interface. There will be more modules that extend this module or use this module
  as a dependency.
  * syscoon_financeinterface_datev_ascii
    * syscoon_partner_accounts
    * syscoon_partner_accounts_automatic
    * syscoon_partner_accounts_automaitc_invoice
    * syscoon_partner_accounts_automaitc_sale
    * syscoon_partner_accounts_automaitc_purchase
    * syscoon_financeinterface_datev_config_skr03
    * syscoon_financeinterface_datev_config_skr04
    * syscoon_financeinterface_datev_import
    * syscoon_financeinterface_datev_xml
  * syscoon_financeinterface_datev_ascii_accounts
  * syscoon_financeinterface_enterprise

Changelog
=========

* 17.0.0.0.5
  * fix problem with journal_id in stead of using journal_ids

* 17.0.0.0.4
  * forwarded from 16.0.0.0.14
  * fix problem with account counterpart computation on bank journals and outstanding payment account

* 17.0.0.0.3
  * forwarded from 16.0.0.0.13
  * add journal_ids to the export views
  * fix expected singleton error on getting payment accounts

* 17.0.0.0.2
  * forwarded from 16.0.0.0.12
  * fix problem with account counterpart computation on bank journals and outstanding payment account

* 17.0.0.0.1
  * initial version
  * ported from 16.0.0.0.10
  * sequence is now created automatically on the first export for each company if it does not exist
  * moved configuration back into accounting configuration below quick_edit_mode

Credits
=======

.. |copy| unicode:: U+000A9 .. COPYRIGHT SIGN
.. |tm| unicode:: U+2122 .. TRADEMARK SIGN

- `Mathias Neef <mathias.neef@syscoon.com>`__ |copy|
  `syscoon <http://www.syscoon.com>`__ |tm| 2024
