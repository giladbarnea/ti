# Features
- [ ] `tf prev` or `tf -` to `on` previous activity
- [ ] Rewrite sheet retroactively if time format changed in cfg
- [ ] `tf rename` to change name of currently worked-on task
- [ ] `tf interrupt [start] [end]` and `tf resume`. if `end` is in the past, automatically `resume`
- [ ] `tf mark`, e.g 'Got to office', isn't continuous

# Bugs
- [ ] Ignores time: `tf on "K8" -t learning 16:50`

# Annoyances
- [ ] `tf on` - 'Already working' since yesterday, auto-finish yesterday and start now

# Need to think through
- Tag activity implicitly if tagged before?

# Performance
- Load store in chunks
