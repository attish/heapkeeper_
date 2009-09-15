# This file is part of Heapkeeper.
#
# Heapkeeper is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Heapkeeper is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Heapkeeper.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (C) 2009 Csaba Hoch
# Copyright (C) 2009 Attila Nagy

"""|hkcustomlib| is a module that can be used to customize Heapkeeper.

Pseudo-types
''''''''''''

|hkcustomlib| has pseudo-types that are not real Python types, but we use them
as types in the documentation so we can talk about them easily.

.. _hkcustomlib_ShouldPrintDateFun:

- **ShouldPrintDateFun(post, genopts)** -- A function that specifies when to
  print the date of a post in the post summary.

  Real type: fun(|Post|, |GeneratorOptions|) -> bool

.. _hkcustomlib_LocaltimeFun:

- **LocaltimeFun(timestamp)** -- A function that calculates the `tm` structure
  based on a timestamp. This means that it converts global time to local time.

  Real type: fun(int), returns time.tm

.. _hkcustomlib_DateOptions:

- **DateOptions** -- Options on how to handle and show dates.

  Real type: {str: object}

  DateOptions keys:

  - `date_format` (str) -- The format of the date as given to `time.strftime`.
  - `postdb` (|PostDB|) -- The post database to work on.
  - `should_print_date_fun` (|ShouldPrintDateFun|) -- The function that
    specifies when to print-the date of a post in the post summary.
  - `timedelta` (datetime.timedelta) -- A date for the post summary will be
    printed if the time between the post and its parent is less then timedelta.
    (If the post has no parent or the date is not specified in each posts, the
    date is printed.)
  - `localtime_fun` (|LocaltimeFun|) -- A function to be used for calculating
    local time when displaying dates.

  Note: this type should be made into a real class, according to the
  :ref:`Options pattern <options_pattern>`.
"""


import os
import time
import datetime
import subprocess

import hkutils
import hklib


##### Date #####

def format_date(post, options):
    """Formats the date of the given post.

    If the post does not have a date, the ``None`` object is returned.

    **Arguments:**

    - `post` (|Post|)
    - `options` (|DateOptions|) -- Required options: date_format, localtime_fun

    **Returns:** str | ``None``
    """

    format = options['date_format']
    localtime_fun = options['localtime_fun']

    timestamp = post.timestamp()
    if timestamp == 0:
        return None
    else:
        return time.strftime(format, localtime_fun(timestamp))

def create_should_print_date_fun(options):
    """Creates a |ShouldPrintDateFun| based on the given options.

    **Arguments:**

    - `post` (|Post|)
    - `options` (DateOptions) -- Required options: postdb, timedelta

    **Returns:** |ShouldPrintDateFun|
    """

    postdb = options['postdb']
    timedelta = options['timedelta']

    def should_print_date_fun(post, genopts):
        parent = postdb.parent(post)
        if not hasattr(genopts, 'section'):
            return True
        if genopts.section.is_flat:
            return True
        if parent == None:
            return True
        if (post.date() != '' and parent.date() != '' and
            (post.datetime() - parent.datetime() >= timedelta)):
            return True
        return False

    return should_print_date_fun

def create_date_fun(options):
    """Creates a |DateFun|.

    **Argument:**

    - `options` (|DateOptions|) -- Required options: date_format, postdb, and
      either:

      - postdb and timedelta, or
      - should_print_date_fun.

    Returns: |DateFun|
    """

    if options['should_print_date_fun'] == None:
        should_print_date_fun = create_should_print_date_fun(options)
    else:
        should_print_date_fun = options['should_print_date_fun']

    def date_fun(post, genopts):
        if should_print_date_fun(post, genopts):
            return format_date(post, options)
        else:
            return None
    return date_fun

def date_defopts(options={}):
    """Returns the default date options."""
    options0 = \
        {'postdb': None,
         'date_format' : '(%Y.%m.%d.)',
         'localtime_fun': time.localtime,
         'should_print_date_fun': None,
         'timedelta': datetime.timedelta(0)}
    options0.update(options)
    return options0

##### Generation #####

def gen_indices(postdb):
    """Generates index pages using the default options.

    **Type:** |GenIndicesFun|
    """

    date_options = date_defopts({'postdb': postdb})
    date_fun = create_date_fun(date_options)
    genopts = hklib.GeneratorOptions()
    genopts.postdb = postdb
    section = hklib.Section('', postdb.all())
    genopts.indices = [hklib.Index([section])]
    hklib.Generator(postdb).gen_indices(genopts)

def gen_threads(postdb):
    """Generates thread pages using the default options.

    **Type:** |GenThreadsFun|
    """

    date_options = date_defopts({'postdb': postdb})
    date_fun = create_date_fun(date_options)
    genopts = hklib.GeneratorOptions()
    genopts.postdb = postdb
    genopts.print_thread_of_post = True
    hklib.Generator(postdb).gen_threads(genopts)

def gen_posts(postdb, posts):
    """Generates post pages using the default options.

    **Type:** |GenPostsFun|
    """

    date_options = date_defopts({'postdb': postdb})
    date_fun = create_date_fun(date_options)
    genopts = hklib.GeneratorOptions()
    genopts.postdb = postdb
    hklib.Generator(postdb).gen_posts(genopts, posts.exp())

##### Misc #####

def default_editor():
    """Returns the default editor of the operating system.

    On Unix systems, the default is ``vi``. On Windows, it is ``notepad``.
    On other operating systems, the function returns ``None.``

    **Returns:** str
    """

    if os.name == 'posix':
        return 'vi'
    elif os.name == 'nt':
        return 'notepad'
    else:
        return None

def edit_files(files):
    """Opens an editor in which the user edits the given files.

    It invokes the editor program stored in the ``EDITOR`` environment
    variable. If ``EDITOR`` is undefined or empty, it invokes the default
    editor on the system using the :func:`default_editor` function.

    **Type:** |EditFileFun|
    """

    old_content = {}
    for file in files:
        old_content[file] = hkutils.file_to_string(file, return_none=True)

    editor = os.getenv('EDITOR')

    # if EDITOR is not set, get the default editor
    if editor is None or editor == '':
        editor = default_editor()

    # if not even the default is set, print an error message
    if editor is None:
        hklib.log(
            'Cannot determine the default editor based on the operating\n'
            'system. Please set the EDITOR environment variable to the editor\n'
            'you want to use or set hkshell.options.callback.edit_files to\n'
            'call your editor of choice.')
        return False

    subprocess.call(editor.split() + files)

    def did_file_change(file):
        new_content = hkutils.file_to_string(file, return_none=True)
        return old_content[file] != new_content

    changed_files = filter(did_file_change, files)
    return changed_files

