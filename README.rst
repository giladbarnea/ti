=================================
Timefred -- A time tracker for optimizing deep focus.
=================================

``Timefred`` is a CLI app that strives to be the Alfred to your Batman.

Basic usage::

    $ tf on 'unit tests'
    $ tf stop

It also understands "natural language" commands, like::

    $ tf on 'unit tests' 30m ago
Fancy report generation::

    $ tf report

Sync with 3rd-party services::

    $ tf sync
``Timefred`` supports a wide range of functionality, including Jira integration, data aggregation, and daemon mode.

Assumptions
====
- No-one wants to do any time tracking.
- Your boss wants you to do all the time tracking.
- You're Batman.

Like the comic book character, ``Timefred`` works by minimizing the user's interaction with it, while
maximizing distraction-free work, and taking care of all the tedious details.

It does this by {describe 'oh-crap I forgot to toggle my timer'}, zero learning curve, "smart" behavior
(doesn't need to be told to do things) like "on" automatically stops the previous timer etc.

Usage
=====
Here's the minimal usage style::

    $ tf on 'unit tests'
    Start working on 'unit tests'.

    $ tf status
    You have been working on 'unit tests' for less than a minute.

    $ tf stop
    Stopped working on 'unit tests'.

    $ tf report
    Thursday April 05 2021
      ...

``on`` and ``stop`` can take arguments for:

- time (format described further down)
- tag
- note
Example::

    $ tf on research 2 hours ago
    Started working on research at 2:40 PM.

    $ tf s
    You have been working on research for about 2 hours (since 2:40 PM).

    $ tf stop 30 minutes ago
    Stopped working on research at 2:10 PM.

Also illustrating in the previous example is short aliases of all commands,
their first letter. Like, ``s`` for ``status``, ``o`` for ``on``,
``f`` for ``stop``, etc.

Put brief notes on what you've been doing::

    $ tf note waiting for Napoleon to take over the world
    $ tf n another simple note for demo purposes

Tag your activities for fun and profit::

    $ tf tag imp

Get a log of all activities with the ``log`` (or ``l``) command::

    $ tf log

Command reference
=================

Run ``tf -h`` (or ``--help`` or ``help`` or just ``h``)
to get a short command summary of commands.

``on``
------

- Short: ``o``
- Syntax: ``tf (o|on) <name> [<time>...]``

Start tracking time for the project/activity given by `<name>`. For example::

    tf on conquest

tells ``tf`` to start tracking for the activity ``conquest`` *now*.
You can optionally specify a relative time in the past like so::

    tf on conquest 10mins ago

The format of the time is detailed further below.

``stop``
-------

- Short: ``f``
- Syntax: ``tf (f|stop) [<time>...]``

End tracking for the current activity *now*. Just like with ``on`` command
above, you can give an optional time to the past. Example::

    tf stop 10mins ago

tells ``Timefred`` that you finished working on the current activity at, well, 10
minutes ago.

``status``
----------

- Short: ``s``
- Syntax: ``tf (s|status)``

Gives short human-readable message on the current status, i.e., whether anything
is being tracked currently or not. Example::

    $ tf on conqering-the-world
    Start working on conqering-the-world.
    $ tf status
    You have been working on `conqering-the-world` for less than a minute.

``tag``
-------

- Short: ``t``
- Syntax: ``tf (t|tag) <tag>...``

This command adds the given tags to the current activity. Tags are not currently
used within the ``Timefred`` time tracker, but they will be saved in the JSON data
file. You may use them for whatever purposes you like.

For example, if you have a script to generate a HTML report from your ``Timefred``
data, you could tag some activities with a tag like ``red`` or ``important`` so
that activity will appear in red in the final HTML report.

Use it like::

    tf tag red for-joe

adds the tags ``red`` and ``for-joe`` to the current activitiy. You can specify
any number of tags.

Tags are currently for your purpose. Use them as you see fit.

``note``
--------

- Short: ``n``
- Syntax: ``tf (n|note) <note-text>...``

This command adds a note on the current activity. Again, like tags, this has no
significance with the time tracking aspect of ``Timefred``. This is for your own
recording purposes and for the scripts your write to process your ``Timefred`` data.

Use it like::

    tf note Discuss this with the other team.

adds the note ``Discuss this with the other team.`` to the current activity.

``log``
-------

- Short: ``l1``
- Syntax: ``tf (l|log) [today]``

Gives a table like representation of all activities and total time spent on each
of them.

Time format
===========

Currently only the following are recognized. If there is something that is not
handled, but should be, please open an issue about it or a pull request
(function in question is ``parse_time``)

- *n* seconds ago can be written as:
    - *n* seconds ago
    - *n* second ago
    - *n* secs ago
    - *n* sec ago
    - *n* s ago
    - ``a`` in place of *n* in all above cases, to mean 1 second.
    - E.g., ``10s ago``, ``a sec ago`` ``25 seconds ago``, ``25seconds ago``.

- *n* minutes ago can be written as:
    - *n* minutes ago
    - *n* minute ago
    - *n* mins ago
    - *n* min ago
    - ``a`` in place of *n* in all above cases, to mean 1 minute.
    - E.g., ``5mins ago``, ``a minute ago``, ``10 minutes ago``.

- *n* hours ago can be written as:
    - *n* hours ago
    - *n* hour ago
    - *n* hrs ago
    - *n* hr ago
    - ``a`` or ``an`` in place of *n* in all above cases, to mean 1 hour.
    - E.g., ``an hour ago``, ``an hr ago``, ``2hrs ago``.

Where *n* is an arbitrary number and any number of spaces between *n* and the
time unit are allowed (including zero spaces).

Inspiration / Alternatives
=====
While building ``Timefred``, I kept `Watson <https://github.com/TailorDev/Watson>`_ in mind for its impressive functionality, and `ti <https://github.com/richmeta/ti>`_ for its simplicity.

`Watson` was awkward to use, and `ti` lacked some features. I wanted something simpler, and more enjoyable to use, that would just let me do my work and not have to worry about the time tracking.

Status
======

The project is in beta. If you find any bug or have any feedback, please do open
`a GitHub issue <https://github.com/giladbarnea/Timefred/issues>`_.


Installation
======


License
=======

MIT License

Content snippets
===============
# You don't have to do anything
- Why does timeBro save so much time? Because you can completely forget time tracking and do it retrospectively in a relaxed manner. For example just before the end of the working day. Or at the end of the week.
- Instead of constantly having to reflect and interrupt during the day, you make time entries only once using the memory aid - efficiently and in one go.
- There are good reasons why many users prefer to estimate their times at the end of the day rather than using stopwatches. Nobody wants to be constantly interrupted by time tracking, because it costs time and focus.
- Thanks to timeBro, these interruptions of the workflow are eliminated - and even the headache of making estimates.

https://upload.wikimedia.org/wikipedia/en/5/5c/Alfred_Pennyworth_%28Alex_Ross%29.jpg