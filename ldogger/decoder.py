#!/usr/bin/env python
# coding: utf-8

import json
import subprocess

# This is a sloppy mix of short (CRIT, WARN, INFO) and long (EMERGENCY, NOTICE)
# should we fix it?
PRIORITY = {
    "0": "EMERGENCY",
    "1": "ALERT",
    "2": "CRIT",
    "3": "ERROR",
    "4": "WARN",
    "5": "NOTICE",
    "6": "INFO",
    "7": "DEBUG",
}

# should we translate facility levels too?
# 0   kern    Kernel messages
# 1   user    User-level messages
# 2   mail    Mail system
# 3   daemon  System daemons
# 4   auth    Security/authentication messages
# 5   syslog  Messages generated internally by syslogd
# 6   lpr     Line printer subsystem
# 7   news    Network news subsystem
# 8   uucp    UUCP subsystem
# 9   cron    Cron subsystem
# 10  authpriv    Security/authentication messages
# 11  ftp     FTP daemon
# 12  ntp     NTP subsystem
# 13  security    Log audit
# 14  console     Log alert
# 15  solaris-cron    Scheduling daemon
# 16–23   local0 – local7     Locally used facilities

XLATE = {
    "_CMDLINE": "cmdline",
    "_EXE": "binary",
    "_TRANSPORT": "log_source",
    "SYSLOG_FACILITY": "facility",
    "_PID": "pid",
    "_UID": "uid",
    "_GID": "gid",
    "_SYSTEMD_CGROUP": "systemd_cgroup",
    "_SYSTEMD_SLICE": "systemd_slice",
    "_SYSTEMD_UNIT": "systemd_unit",
    "_BOOT_ID": "boot_id",
    "_MACHINE_ID": "machine_id",
    "ERRNO": "errno",
}


def _decode_journald_json(args, x):
    x = json.loads(x)

    args.msg = (x["MESSAGE"],)

    for lhs, rhs in XLATE.items():
        if v := x.get(lhs, None):
            args.meta[rhs] = v

    for k in ("_SYSTEMD_UNIT", "SYSLOG_IDENTIFIER"):
        try:
            args.app = x[k]
            if args.app.endswith(".service"):
                # the UNIT is only preferable to the syslog identifier when
                # we're talking about a service (not e.g. session-3.slice)
                break
        except KeyError:
            pass

    p = x.get("PRIORITY", "6")
    args.level = PRIORITY.get(p, p)

    # NOTE: now will be interpreted by the argument parsing as the d.send(now=)
    # field rather than an actual meta field
    for k in ("_SOURCE_REALTIME_TIMESTAMP", "__REALTIME_TIMESTAMP"):
        try:
            args.meta["now"] = int(x[k])
            break
        except (TypeError, KeyError, ValueError):
            pass

    return args


def decode_journald_json(args, x):
    try:
        return _decode_journald_json(args, x)
    except:
        p = subprocess.Popen(["jq", "."], stdin=subprocess.PIPE)
        p.communicate(x.encode())
        raise
