# log2dna gadgets

I'm used to Splunk, but it costs too much for personal use. logdna seems kinda
cute, but there doesn't seem to be much in the way of tools to use.

# what are we doing here?

## ldogger

I started trying to make a generic log collection tool, but I stopped short of
building an entire parsing forwarder thingy... I was frustrated that I didn't
have a way to deal with slurping the app name from the log line (you know, so
the app isn't always "ldogger" and in fact reflects the collected line).

Specifying `--app blah` is fine if all the logs you're collecting relate to
'blah', otherwise it kinda sucks... so I made this weird semi-recursive
re-arg-parsing regex-trick-engine that allows redefinition of collected
commandline switches based on regex matches.

This all got rather complicated, so I got bored with it.

## sj2l

What I really wanted in the end was a system to collect journald json output,
reparse it slightly and forward that. And I didn't need a lot of options to
re-arrange things cuz the fields are already pretty predictable.

Rather than find some way to kludge json parsing into the above already
too-complicated ldogger thingy, I made a new thingy whose dedicated purpose is
to collect journald logs and reformat them predictably for logdna ...

... I think this half-assed solution sorta fits the bill.

(oh: sj2l means systemd-journald =to=> logdna)

# not really proud of this

Most of the code in this repo is a total mess. I think I kinda like sj2l, so I
might refactor this repo a bit at some point to focus on that. On the other hand
I may keep ldogger too. I may combine them.  I just havne't decided what to do,
but if you look in ldogger/args.py you'll see my mixed feelings manifest as some
pretty scatterbrained BS.
