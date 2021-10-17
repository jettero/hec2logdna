# log2dna gadgets


## hubble.py

I specifically wanted this so I wouldn't have to run a development Splunk while
testing development of Hubble. While logdna definitely can't do the remarkable
things Splunk does, it also doesn't need a license refresh every 6 months and
doesn't cost more than my car for a tiny sized instance (I mean, if you don't
wanna deal with developer licensing).

So this hubble.py ... it's hubble specific in a lot of ways... I wish to make a
more generic ... hrm...

# todo

* make a generic collector with plugins for noticing and reacting to types
  (e.g., hubble)

* make a hubble plugin

* make a plugin for the slick json output of journald and a log tail mechanism
  thereto
