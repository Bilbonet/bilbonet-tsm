================================
TSM tasks timesheet time control
================================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1| |badge2|

* Each employee can encode and track their time spent on the different
  tasks.
* This module adds a button at task time line level to compute the spent
  time, in minutes, from start date to the current moment.
* Finally, it allows to open and close tasks from account analytic lines.
  The selected closed stage is the first one that is found with the mark
  "Closed" checked.

**Table of contents**

.. contents::
   :local:

Usage
=====

You can access via timesheets:

#. Go to *Timesheets > Timesheet > All Timesheets*.
#. Create a new record.
#. You will see now that the "Date" field contains also time information.
#. If you don't select any "project", you will be able to select any "task",
   opened or not.
#. Selecting a "task", the corresponding "project" is filled.
#. Selecting a "project", tasks are filtered for only allow
   to select opened tasks for that project. Remember that an opened task is
   a task whose stage doesn't have "Closed" mark checked.
#. At the end of the line, you will see an stop button.
#. When you press this button, the difference between "Date" field and the
   current time, writing this in the field "Duration".
#. You can modify the "Date" field for altering the computation of the
   duration.

Or via tasks:

#. Go to Project > Search > Tasks.
#. Click on one existing task or create a new one.
#. On the "Timesheets" page, you will be able to handle records the same way
   as you do in the above explanation (except the task selection part, which
   in this case doesn't appear as it's the current one).

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/project/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://github.com/OCA/project/issues/new?body=module:%20project_timesheet_time_control%0Aversion:%2011.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* bilbonet.NET

Contributors
~~~~~~~~~~~~

* `Bilbonet <https://www.bilbonet.net>`_:

    * Jesus Ramiro

Maintainers
~~~~~~~~~~~

This module is maintained by Bilbonet.


This module is part of the `Bilbonet/bilbonet-tsm <https://github.com/Bilbonet/bilbonet-tsm/tree/11.0>`_ on GitHub.

