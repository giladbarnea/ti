=================================
Timefred -- Not a silly simple time tracker
=================================

``Timefred`` is a small command line time-tracking application.
Simple basic usage looks like this::

    $ tf on my-project
    $ tf stop

You can also give it human-readable times::

    $ tf on my-project 30mins ago

``Timefred`` sports many other cool features. Read along to discover.

Wat?
====

``Timefred`` is a simple command line time tracker. It has been completely rewritten
in Python (originally a bash script) and has (almost) complete test coverage. It
is inspired by `timed <http://adeel.github.com/timed>`_, which is a nice project
that you should check out if you don't like ``Timefred``. ``Timefred`` also takes
inspiration from the simplicity of `t <http://stevelosh.com/projects/t/>`_.

If a time-tracking tool makes me think for more than 3-5 seconds, I lose my line
of thought and forget what I was doing. This is why I created ``Timefred``. With
``Timefred``, you'll be as fast as you can type, which you should be good with anyway.

The most important part about ``Timefred`` is that it provides just a few commands to
manage your time-tracking and then gets out of your way.

All data is saved in a JSON file ,``~/.tf-sheet``. (This can be changed using the
``$SHEET_FILE``  environment variable.) The JSON is easy to access and can be
processed into other more stylized documents. Some ideas:

- Read your JSON file to generate beautiful HTML reports.
- Build monthly statistics based on tags or tasks.
- Read your currently working project and display it in your terminal prompt.
  Maybe even with the number of hours you've been working.

It's *your* data.

Oh and by the way, the source is a fairly small Python script, so if you know
Python, you may want to skim over it to get a better feel of how it works.

*Note*: If you have used the previous bash version of ``Timefred``, which was horribly
tied up to only work on Linux, you might notice the lack of plugins in this
Python version. I am not really missing them, so I might not add them. If anyone
has any interesting use cases for it, I'm willing to consider.

Usage
=====

Here's the minimal usage style::

    $ tf on my-project
    Start working on my-project.

    $ tf status
    You have been working on my-project for less than a minute.

    $ tf stop
    So you stopped working on my-project.

``on`` and ``stop`` can take a time (format described further down) at which to
apply the action::

    $ tf on another-project 2 hours ago
    Start working on another-project.

    $ tf s
    You have been working on another-project for about 2 hours.

    $ tf stop 30 minutes ago
    So you stopped working on another-project.

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

Status
======

The project is in beta. If you find any bug or have any feedback, please do open
`a GitHub issue <https://github.com/tbekolay/Timefred/issues>`_.


Gimme!
======

You can download ``Timefred`` `from the source on
GitHub <https://raw.github.com/giladbarnea/timefred/master/bin/Timefred>`_.

- Put it somewhere in your ``$PATH`` and make sure it has executable permissions.
- Install ``pyyaml`` using the command ``pip install --user pyyaml``.
- Install ``colorama`` using the command ``pip install --user colorama``.

After that, ``Timefred`` should be working fine.

Also, visit the `project page on GitHub <https://github.com/giladbanrea/timefred>`_ for
any further details.

Who?
====

Originally created and fed by Shrikant Sharat
(`@sharat87 <https://twitter.com/#!sharat87>`_).
Now forked and maintained by Gilad Barnea
(`@tbekolay <https://github.com/giladbarnea>`_) on GitHub.

License
=======

`MIT License <http://mitl.sharats.me>`_.
