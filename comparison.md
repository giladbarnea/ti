# Timefred
Automatically track, display and submit your work to Jira, with customizable hooks to local commands (`git`, `docker`, ...) and advanced report filtering.


# Why?
I think it's ironic that it takes time and effort to log your time and effort.

Plus I hate context switching.

When I work, I frequently jump between different branches, dirs and projects. 

Making sense out of this chaos in retrospect (e.g figuring out how many minutes I spent on which sub-task 2 days ago, before lunch) is painful and should be automated.

# So many time tracking tools out there though...
That's true. 

All the tools I've used feel like they manage _me_ in some sense. I need to report to _them_, and do things in a such a way that their logs make sense at the end of the day.

`timefred` is built with the assumption that you can do whatever you want, as long as you get the job done.

Remembering to announce the moment you start or stop working, or needing to edit entries, is just another form of work.

# What it does
It decorates terminal actions of your choice, displays a high-resolution aggregation of your work, and submits it to Jira. 

# Comparison with existing tools
| Tool                         | Jira integration | Doesn't need you | Flexible reports | Past / Future tense support | Zsh integration | Notes         |
| ---------------------------- | ---------------- | ---------------- | ---------------- | --------------------------- | --------------- | ------------- |
| `timefred`                   | V                | V                | V                | V                           | V               |               |
| [`dob`][dob]                 | ?                | ?                | ?                | ?                           | ?               |               |
| [`did`][did]                 | X                | X                | V                |                             | X               |               |
| [`i-did`][i-did]             | X                | X                | X                |                             | X               |               |
| [`yatta`][yatta]             | X                | X                | X                |                             | V               |               |
| [`ttrack`][ttrack]           | X                | X                | V                | V                           | X               |               |
| [`timetracker`][timetracker] | X                | X                | X                |                             | X               |               |
| [`utt`][utt]                 | X                | X                | V                |                             | X               | Fancy reports |
| [`ti`][ti]                   | X                | X                | V                | V                           | X               |               |
| [`hamster-cli`][hamster-cli] |                  |                  |                  |                             |                 |               |
| [`ctt`][ctt]                 | X                | X                | V                |                             | X               |               |
| [`tasklog`][tasklog]         | V                | X                | V                | X                           | X               |               |
| [`jtime`][jtime]             | V                | X                |                  |                             |                 |               |


# What `timefred` is not
`timefred` is not a task manager, nor a stopwatch wrapper.

In other words, it doesn't require defining a specific Jira or repo, and it doesn't have a "start" / "stop" functions.


# Other projects
Tools with different goals.
[`hamster-bridge`](https://pypi.org/project/hamster-bridge/)
[`project-hamster`](https://github.com/projecthamster)
[`termdown`](https://github.com/trehn/termdown)
[`timetrack`](https://www.flathub.org/apps/details/net.danigm.timetrack)
[`timetrap`](https://github.com/samg/timetrap)
[`timewarrior`](https://timewarrior.net/) - Timer
[`Watson`](https://github.com/TailorDev/Watson) - Timer
[`Wakatime`](https://wakatime.com) - Passive IDE Plugin for code stats, many integrations (BB, GH etc)
[`worklog`](https://dcs-worklog.readthedocs.io/en/latest/index.html) - Timer
[`worklogmd`](https://pypi.org/project/worklogmd/) - Only prints, no adding entries
[`t`](https://stevelosh.com/projects/t/) - Task manager
[`timed`](http://adeel.github.io/timed/) - Timer
[`tt-cli`](https://pypi.org/project/tt-cli/) - Just sums up "add"
[`mttt`](https://pypi.org/project/mttt/) - Timer and task manager, Python2 only
[`spendtime`](https://pypi.org/project/spendtime/) - Timer
[`salary-timetracker`](https://pypi.org/project/salary-timetracker/) - Salary calculator
[`time-tracker-plus`](https://pypi.org/project/time-tracker-plus/) - Mostly reporting
[`time-tracker-cli`](https://pypi.org/project/time-tracker-cli/) - Half baked
[`timetracker-cli`](https://pypi.org/project/timetracker-cli/) - For Bairesdev TimeTracker

[did]: (https://pypi.org/project/did/)
[dob]: (https://pypi.org/project/dob/)
[hamster-cli]: (https://github.com/rhroberts/hamster-cli)
[i-did]: (https://pypi.org/project/i-did)
[ti]: (https://github.com/richmeta/ti)
[time-tracker]: (https://pypi.org/project/time-tracker/)
[timetracker]: (https://pypi.org/project/timetracker/)
[tt-time-tracker]: (https://pypi.org/project/tt-time-tracker/)
[ttrack]: (https://pypi.org/project/ttrack/)
[utt]: (https://github.com/larose/utt)
[yatta]: (https://github.com/rhroberts/yatta)
[watson-jira]: (https://pypi.org/project/watson-jira/)
[jtime]: (https://pypi.org/project/jtime/)
[tasklog]: (https://pypi.org/project/tasklog/)
[ctt]: (https://code.ungleich.ch/ungleich-public/ctt/-/blob/master/ctt.text)

