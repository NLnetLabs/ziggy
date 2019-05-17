# Ziggy: the RPKI Wayback Machine

**Copyright (c) 2019 NLnet Labs (https://nlnetlabs.nl/)**

All rights reserved. Distributed under a 3-clause BSD-style license. For more information, see LICENSE

## Preamble

The current Ziggy scripts are developed to run against the raw unfiltered data collected by RIPE NCC. Once we turn this into a git repository, we may want to derive a public version of the scripts that works against that.

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
 - `vrp-out-name` -- output filename for VRP data, {} is replace by the date in ISO notation (e.g. 2018-01-01)
 - `ignore-tals` -- a list of repositories for which Ziggy should not generate a TAL, even if a TA certificate is available

A sample file called `sample-ziggy.conf` is included in the repository.

### Running

Running Ziggy is as simple as invoking:

```
$ ./ziggy.py -c <config-file> -d <date-in-ISO>
```

Where `<date-in-ISO>` is the date for which to extract data in ISO notation (e.g. 2018-01-01 for January 1st, 2018).

Currently, Ziggy outputs the highest observed timestamp in the RIPE `.tgz` archives for that date, you can use this as the data to pass to `faketime`, below is an example of the output:

```
Highest timestamp found: 2018-01-01 05:30:55
```

To run Routinator in this example would mean invoking it as follows:

```
$ faketime '2018-01-01 05:30:55' routinator vrps -n
```

## TODO

 - Actually invoke Routinator