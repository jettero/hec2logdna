# log2dna gadgets

I'm used to Splunk, but it costs too much for personal use. log2dna seems kinda
cute, but there doesn't seem to be much in the way of tools to use.

## todo

* generic collector with plugins for noticing and reacting to types
  * make a hubble plugin
  * make a journald jso

* make a plugin for the slick json output of journald and a log tail mechanism
  thereto

## hubble.py

This thing pretends to be a HEC endpoint, fixes up some of the hubble data
fields and forwards the logs to logdna.
