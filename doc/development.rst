Development
===========

This page describes the development methods and the tools that are used.

Development method
------------------

There are some rules to follow when developing Heapkeeper.
These are described in the :doc:`developmentrules`.
About more specific conventions regarding the documentation and the source
code, see :doc:`codingconventions`.

Reading
^^^^^^^

* `Producing Open Source Software -- How to Run a Successful Free
  Software Project by Karl Fogel`__: A book that gives a lot of practical
  advice to the kinds of projects we are.
* `The Elements of Style by William Strunk, Jr.`__: A book that helps write
  in good English style.

__ http://producingoss.com/
__ http://en.wikisource.org/wiki/The_Elements_of_Style

Development tools
^^^^^^^^^^^^^^^^^

All the development tools we use are free and open source programs.

The following programs should be installed on a developer's computer: Python_,
Git_, Sphinx_ and reStructuredText_.

Python
""""""

Python_ is the interpreter that executes Heapkeeper. Heapkeeper needs Python
2.5 or 2.6.

.. _`Python`: http://www.python.org/

Git
"""

Git_ is version control system that we use to manage the source code and
documentation of Heapkeeper. These are stored in the `Heapkeeper repository`_,
which is hosted by GitHub_. We use Git 1.6, but probably previous versions are
probably fine.

.. _`Git`: http://git-scm.com/
.. _`GitHub`: http://github.com/
.. _`Heapkeeper repository`: http://github.com/hcs42/heapkeeper/

Sphinx
""""""

The documentation is written in reStructuredText_ format and is generated by
the Sphinx_ program.

In order to use Sphinx, first install Mercurial_, which is a distributed
version control system used by Sphinx. Then download and install the
b494914e054a revision from the `Sphinx repository`_. For Unix users:

.. code-block:: sh

    $ hg clone http://bitbucket.org/birkenfeld/sphinx/
    $ cd sphinx
    $ hg up -r b494914e054a
    $ python setup.py build
    $ sudo python setup.py install

Notes:

- ``hg`` is the command that executes Mercurial.
- The Sphinx revision we use may change in the future. In this case, an email
  will be sent to the Heapkeeper heap, and this page will be updated.

The format defined by reStructuredText_ and Sphinx_ is not trivial. Two pages
that are worth to have a look at:

* `Sphinx documentation`_
* `reStructuredText Quick Reference`_

.. _`reStructuredText`: http://docutils.sourceforge.net/rst.html
.. _`Sphinx`: http://sphinx.pocoo.org/
.. _`Mercurial`: http://mercurial.selenic.com/
.. _`Sphinx repository`: http://bitbucket.org/birkenfeld/sphinx/
.. _`Sphinx documentation`: http://sphinx.pocoo.org/contents.html
.. _`reStructuredText Quick Reference`:
   http://docutils.sourceforge.net/docs/user/rst/quickref.html

Communication
-------------

We use a heap to communicate. The development heap will become public when
we feel that Heapkeeper is in a stage to support maintaining a public heap.
Until then, you can contact us via email as described on the
`index page <index>`.

The :doc:`todo` file is our "bug and feature tracking" system that we use to
track the bugs we find and features that we want to implement.

Content of the repository
-------------------------

The main directories and files in Heapkeeper's repository:

``README``
  Usual README file.
``doc``
  Documentation files. The ``rst`` files are text files with wiki-like syntax,
  and Sphinx can be used to generate HTML or other output from them.
``doc/todo.rst``
   Our feature and bug tracking "system".
``*.py``
   Python source files -- Heapkeeper itself
``heapindex.css``
   A CSS file for the generated HTML files.
