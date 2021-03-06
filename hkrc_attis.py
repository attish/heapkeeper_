# -*- coding: utf-8 -*-

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

# Copyright (C) 2009 Attila Nagy
# Copyright (C) 2009 Csaba Hoch

"""My (Attis) hkrc."""

import hklib
import hkshell
import hkcustomlib
import hkutils
import subprocess
import time
import datetime
import re

def overquoted(post):
    all = 0
    quoted = 0
    for line in post.body().splitlines():
        all += 1
        if re.search('^\s*\>', line):
            quoted += 1
    return 100 * quoted / all > 70

def date_fun(post, options):
    root = post._postdb.root(post)
    if hasattr(options, 'section'):
        section = options.section
        if section.is_flat or \
           root == post:
            return format_date(post)
    if post.date() != '' and root.date() != '':
        diff = read_date(post) - read_date(root)
        if diff.days > 0:
            return '(+%d days)' % diff.days
        elif diff.seconds > 3600:
            return '(+%d hours)' % (diff.seconds / 3600)
        elif diff.seconds > 60:
            return '(+%d minutes)' % (diff.seconds / 60)
        else:
            return None
    else:
        return "(nincs dátum!)"

def sections(postdb):
    exp = False
    eliminate = False

    # ps_all = összes levél
    ps_all = postdb.all().copy()

    # ps_attention = unanswered proposals
    # ps_singles = all other mail w/o answers
    ps_singles = postdb.roots()
    for post in postdb.all():
        ps_singles -= hklib.PostSet(postdb, [postdb.parent(post)])
    ps_attention = ps_singles.collect.has_tag('prop')
    ps_singles -= ps_attention

    # tidy
    # posts that belong here either:
    # * contain quote introduction (like "xyz wrote:")
    # * contain more quote lines than non-quote
    ps_tidy = ps_all.collect.body_contains('\>*\s*2([0-9]+\/)+[0-9]+\s*.*\<[a-z.-]+@[a-z.-]+\>')
    ps_tidy |= ps_all.collect.body_contains('wrote:')
    ps_tidy |= [post for post in postdb.all() if overquoted(post)]
    ps_tidy -= ps_all.collect.has_tag('reviewed')

    # todo
    ps_todo = ps_all.collect.has_tag('todo')
    ps_todo |= ps_all.collect.body_contains("^<<<\!*todo")

    # heap
    ps_heap = ps_all.collect.has_tag('heap')
    if exp:
        ps_heap = ps_heap.exp()
    if eliminate:
        ps_all -= ps_heap

    # programozás
    ps_prog = ps_all.collect.has_tag_from(('Programozás', 'programozás'))
    if exp:
        ps_prog = ps_prog.exp()
    if eliminate:
        ps_all -= ps_prog

    # C és C++ programozás
    ps_ccpp = ps_all.collect.has_tag_from(('c', 'C', 'c++', 'C++'))
    if exp:
        ps_ccpp = ps_ccpp.exp()
    if eliminate:
        ps_all -= ps_ccpp

    # Python programozás
    ps_py = ps_all.collect.has_tag_from(('python', 'Python'))
    if exp:
        ps_py = ps_py.exp()
    if eliminate:
        ps_all -= ps_py

    # politika
    ps_pol = ps_all.collect.has_tag_from(('politika', 'Politika'))
    if exp:
        ps_pol = ps_pol.exp()
    if eliminate:
        ps_all -= ps_pol

    res = [ hklib.Section("Nyitott javaslatok", ps_attention, {'flat': True}),
            hklib.Section("Takarítani", ps_tidy, {'flat': True}),
            hklib.Section("Tennivalók", ps_todo, {'flat': True}),
            hklib.Section("Cipősdoboz", ps_singles, {'flat': True}),
            hklib.Section("Heap", ps_heap),
            hklib.Section("Programozás", ps_prog),
            hklib.Section("C és C++", ps_ccpp),
            hklib.Section("Python", ps_py),
            hklib.Section("Egyéb", ps_all)]
    # monthly = do_monthly(postdb)
    # if monthly != None:
    #     res.extend(monthly)
    return res

def get_date_limits(postdb):
    "Gets the datetime of the earliest and newest posts in postdb."
    start_date, end_date = None, None
    for post in postdb.roots():
        if start_date == None:
            start_date = read_date(post)
        if end_date == None:
            end_date = read_date(post)
        else:
            if start_date > read_date(post):
                start_date = read_date(post)
            if end_date < read_date(post):
                end_date = read_date(post)
    return (start_date, end_date)

def get_month(year, month):
    months = ['január', 'február', 'március', 'április', 'május', 'június', 'július', \
        'augusztus', 'szeptember', 'október', 'november', 'december']
    return "%d %s" % (year, months[month - 1])

def get_posts_in_month(postdb, year, month):
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_year += 1
        next_month = 1
    return postdb.postset([post._heapid for post in postdb.roots() \
        if post.date() != '' \
            and read_date(post) > datetime.datetime(year, month, 1) \
            and read_date(post) < datetime.datetime(next_year, next_month, 1)])

def do_monthly(postdb):
    start_date, end_date = get_date_limits(postdb)
    curr_year, curr_month = start_date.year, start_date.month
    monthlist = []
    while datetime.datetime(curr_year, curr_month,1) < end_date:
        monthlist.append((get_month(curr_year, curr_month), \
            get_posts_in_month(postdb, curr_year, curr_month)))
        curr_month += 1
        if curr_month == 13:
            curr_year += 1
            curr_month = 1
    return [hklib.Section(*month) for month in monthlist]

def format_date(post):
    "post -> str"
    if post.date() == '':
        return "(no date)"
    else:
        d = time.localtime(hkutils.calc_timestamp(post.date()))
        return "(" + time.strftime('%Y.%m.%d.', d) + ')'

def read_date(post):
    "post_date -> datetime.datetime"
    if post.date():
        return datetime.datetime.fromtimestamp(
                hkutils.calc_timestamp(post.date())
            )
    else:
        return None

def gen_indices(postdb):

    # Date options
    #date_options = hkcustomlib.date_defopts()
    #date_options.update({'postdb': postdb,
    #                     'timedelta': datetime.timedelta(days=0)})
    #date_fun = hkcustomlib.create_date_fun(date_options)

    # Generator options
    genopts = hklib.GeneratorOptions()
    genopts.postdb = postdb
    #    genopts.indices = [hklib.Index(sections(postdb)), hklib.Index(do_monthly(postdb),"monthly.html")]
    # new idea is:
    # - add static main index,
    # - do_montly() and store its results,
    # - iterate on months, add one new index per month, one section per index

    genopts.indices = [hklib.Index(sections(postdb))]
    #months = do_monthly(postdb)
    #for n in range(0, len(months)):
    #    genopts.indices.append(hklib.Index([months[n]],
    #                           "month_" + str(n + 1) + ".html"))

    genopts.write_toc = True
    genopts.shortsubject = True
    genopts.shorttags = True
    genopts.date_fun = date_fun

    # Generating the index
    hklib.Generator(postdb).gen_indices(genopts)

def gen_posts(postdb, posts):
    # Generator options
    date_options = hkcustomlib.date_defopts()
    date_options.update({'postdb': postdb,
                         'timedelta': datetime.timedelta(days=0)})
    date_fun = hkcustomlib.create_date_fun(date_options)

    genopts = hklib.GeneratorOptions()
    genopts.postdb = postdb
    genopts.write_toc = True
    genopts.print_thread_of_post = True
    genopts.date_fun = date_fun

    # Generating the posts
    hklib.Generator(postdb).gen_posts(genopts, posts)

@hkshell.hkshell_cmd()
def et(pps):
    """Tidy up a whole thread."""
    roots = []
    for post in hklib.PostSet(hkshell.postdb(), pps):
        roots.append(hkshell.postdb().root(post))
    for root in roots:
        for post in hkshell.postdb().iter_thread(root):
            hkshell.e(post.heapid())
    hkshell.ga()

@hkshell.hkshell_cmd()
def lsr(heapid):
    """Print a whole thread, ie. recursive ls."""
    hkshell.ls(hkshell.ps(heapid).exp())

hkshell.options.callbacks.gen_indices = gen_indices
hkshell.options.callbacks.gen_posts = gen_posts
hkshell.on('save')
