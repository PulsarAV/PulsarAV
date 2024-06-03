============================================
syscoon Finanzinterface - DATEV ASCII Export
============================================

Installation
============

To install this module, you need to:

Go to apps and search for syscoon Finanzinterface - DATEV ASCII Export

Usage
=====

*

Changelog
=========

* 17.0.0.0.4
  * forwarded 16.0.0.0.18
  * add journal_ids to the export view

* 17.0.0.0.3
  * forwarded 16.0.0.0.16 + 16.0.0.0.17
  * change exchange rate digits to round to 4 and add "00"
  * solve problems with reconciled entries and and the output of Belegfeld 1

* 17.0.0.0.2
  * solve "no operator" error if sequence not exists when creating new export record

* 17.0.0.0.1
  * initial version
  * ported from 16.0.0.0.12
  * move grouping lines by journal back to res.config.settings as many2many

Credits
=======

.. |copy| unicode:: U+000A9 .. COPYRIGHT SIGN
.. |tm| unicode:: U+2122 .. TRADEMARK SIGN

- `Mathias Neef <mathias.neef@syscoon.com>`__ |copy|
  `syscoon <http://www.syscoon.com>`__ |tm| 2024
