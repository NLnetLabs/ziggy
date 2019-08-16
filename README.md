# Ziggy: the RPKI Wayback Machine

**Copyright (c) 2019 NLnet Labs (https://nlnetlabs.nl/)**

All rights reserved. Distributed under a 3-clause BSD-style license. For more information, see LICENSE

## Dependencies

Ziggy requires Python 3 to run, and has been tested with Python 3.6 on Ubuntu 18.04LTS. 

Note that the script also requires the Python ```dateutil``` package to be installed. This is available for most distributions as a native package, for example, on an Ubuntu system the following command installs this package:

```
$ apt install python3-dateutil
```

## Running Ziggy

### Configuration file

Ziggy uses a very simple configuration file in JSON format. Currently, the following keys should be defined in the config:

 - `repo-archive-dir` -- the directory where the RIPE `.tgz` files are located
 - `routinator` -- the full path to the `routinator` executable to run
 - `routinator-cache` -- path to the Routinator repository cache
 - `routinator-tals` -- path to the Routinator TAL cache
 - `vrp-out-format` -- output format to ask Routinator for
 - `vrp-out-name` -- output filename for VRP data, {} is replaced by the date in ISO notation (e.g. 2018-01-01)
 - `routinator-log-name` -- filename for the log, {} is replaced by the date in ISO notation
 - `ignore-tals` -- a list of repositories for which Ziggy should not generate a TAL, even if a TA certificate is available

A sample file called `sample-ziggy.conf` is included in the repository.

### Running

Running Ziggy is as simple as invoking:

```
$ ./ziggy.py -c <config-file> -d <date-in-ISO>
```

Where `<date-in-ISO>` is the date for which to extract data in ISO notation (e.g. 2018-01-01 for January 1st, 2018).

Ziggy will end by running the Routinator. It shows you the command line it uses to invoke Routinator so you can easily re-run Routinator if you wish to.
