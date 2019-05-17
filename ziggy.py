#!/usr/bin/env python3
#
# Ziggy: makes quantum leaps through RPKI history
# Copyright (c) 2019 NLnet Labs
# See LICENSE (TL;DR: 3-clause BSD)

import os
import sys
import argparse
import datetime
import dateutil.parser
import tarfile
import gzip
import shutil
import simple_config as sc

def process_date(day):
    print('Ziggy is processing data for {}'.format(day))

    # Step 1: find the tar archives for the specified date
    search_path = sc.get_path_item('repo-archive-dir')

    day_tarfiles = []

    for name in os.listdir(search_path):
        if str(day) in name:
            day_tarfiles.append(name)
            print('Ziggy found {}'.format(name))

    # Step 2: clean out the Routinator cache and TAL directory
    routinator_cache = sc.get_path_item('routinator-cache')
    routinator_tals = sc.get_path_item('routinator-tals')

    try:
        sys.stdout.write('Cleaning out {} ... '.format(routinator_cache))
        sys.stdout.flush()
        shutil.rmtree(routinator_cache)
        os.mkdir(routinator_cache)
        print('OK')

        sys.stdout.write('Cleaning out {} ... '.format(routinator_tals))
        sys.stdout.flush()
        shutil.rmtree(routinator_tals)
        os.mkdir(routinator_tals)
        print('OK')
    except Exception as e:
        print('FAILED')
        raise e

    # Step 3: extract the unvalidated data from the tar archives
    ignore_tals = sc.get_config_item('ignore-tals')
    latest_time = datetime.datetime.fromtimestamp(0)

    for tarchive in day_tarfiles:
        sys.stdout.write('Ziggy is processing {} ... '.format(tarchive))
        sys.stdout.flush()
        obj_count = 0

        try:
            t = tarfile.open('{}/{}'.format(sc.get_path_item('repo-archive-dir'), tarchive))
            basepath = None
            wrote_ta = False

            for member in t:
                if '/unvalidated/' in member.name and member.isfile():
                    pathcomp = member.name.split('/')

                    i = 0

                    while pathcomp[i] != 'unvalidated':
                        i += 1

                    i += 1

                    write_path = '{}/{}'.format(routinator_cache, '/'.join(pathcomp[i:-1]))
                    if basepath == None:
                        basepath = pathcomp[i]
                    
                    try:
                        os.makedirs(write_path)
                    except:
                        pass

                    out_fd = open('{}/{}'.format(write_path, pathcomp[-1]), 'wb')

                    in_fd = t.extractfile(member)

                    buf = in_fd.read(1024)

                    while len(buf) > 0:
                        out_fd.write(buf)
                        buf = in_fd.read(1024)

                    out_fd.close()
                    in_fd.close()
                    obj_count += 1

                    if datetime.datetime.fromtimestamp(member.mtime) > latest_time:
                        latest_time = datetime.datetime.fromtimestamp(member.mtime)
                elif member.name.endswith('.tal.cer') and member.isfile():
                    if wrote_ta:
                        raise Exception("Already wrote a TA for {}, wasn't expecting another one.".format(tarchive))

                    out_fd = open('{}/tmp-ta.cer'.format(routinator_cache), 'wb')

                    in_fd = t.extractfile(member)

                    buf = in_fd.read(1024)

                    while len(buf) > 0:
                        out_fd.write(buf)
                        buf = in_fd.read(1024)

                    out_fd.close()
                    in_fd.close()
                    wrote_ta = True
    
            print('OK ({} objects)'.format(obj_count))

            if not wrote_ta:
                print('Warning, found no TA in {}'.format(tarchive))
            else:
                if basepath in ignore_tals:
                    print('Ignoring TAL for {}'.format(basepath))
                    os.unlink('{}/tmp-ta.cer'.format(routinator_cache))
                else:
                    # For some older archives, the TA certificate is
                    # sometimes encoded in PEM format. Convert it to
                    # DER if necessary
                    ta_fd = open('{}/tmp-ta.cer'.format(routinator_cache), 'rb')
                    is_pem = False
                    pem_header = bytes('-----BEGIN CERTIFICATE-----', 'utf8')

                    for line in ta_fd:
                        if len(line) >= len(pem_header) and line[:len(pem_header)] == pem_header:
                            is_pem = True
                            break

                    ta_fd.close()

                    if is_pem:
                        print('Found an old TA certificate in PEM format, converting to DER')
    
                        osslcmd = 'openssl x509 -inform PEM -in {}/tmp-ta.cer -outform DER -out {}/tmp-ta-der.cer'.format(routinator_cache, routinator_cache)
    
                        if os.system(osslcmd) != 0:
                            raise Exception("Fail to convert TA from PEM to DER")
    
                        os.unlink('{}/tmp-ta.cer'.format(routinator_cache))
                        os.rename('{}/tmp-ta-der.cer'.format(routinator_cache), '{}/tmp-ta.cer'.format(routinator_cache))

                    # Move the TA in place
                    ta_name = 'ta.cer'
                    tal_name = "{}.tal".format(basepath)

                    if 'apnic' in tarchive:
                        fields = tarchive.split('.')

                        for field in fields:
                            if field.startswith('apnic'):
                                ta_name = 'ta-{}.cer'.format(field)
                                tal_name = '{}-{}.tal'.format(basepath, field)

                    ta_path = '{}/{}/ta'.format(routinator_cache, basepath)
                    sys.stdout.write('Moving TA to {}/{} ...'.format(ta_path, ta_name))
                    sys.stdout.flush()
    
                    try:
                        os.makedirs(ta_path)
                    except:
                        pass
    
                    os.rename('{}/tmp-ta.cer'.format(routinator_cache), '{}/{}'.format(ta_path, ta_name))
                    print('OK')
    
                    sys.stdout.write('Creating a TAL for this TA ... ')
                    sys.stdout.flush()

                    tal = open('{}/{}'.format(routinator_tals, tal_name), 'w')
                    tal.write('rsync://{}/ta/{}\n\n'.format(basepath, ta_name))
                    tal.close()
    
                    osslcmd = "openssl x509 -inform DER -in {}/{} -pubkey -noout | awk '!/-----(BEGIN|END)/' >> {}/{}".format(ta_path, ta_name, routinator_tals, tal_name)
    
                    if os.system(osslcmd) != 0:
                        print('FAILED')
                        raise Exception('Failed to create a TAL')
    
                    print('OK')
        except Exception as e:
            print('Failed to process {}'.format(tarchive))
            raise e

    print('Highest timestamp found: {}'.format(latest_time))

def main():
    argparser = argparse.ArgumentParser(description='Make quantum leaps through RPKI history')

    argparser.add_argument('-c, --config', nargs=1, help='configuration file to use', type=str, metavar='config_file', dest='config_file', required=True)
    argparser.add_argument('-d, --date', nargs=1, help='date to process', type=str, metavar='process_date', dest='process_date', required=True)

    args = argparser.parse_args()

    try:
        sc.load_config(args.config_file[0])
    except Exception as e:
        print('Failed to load the configuration from {} ({})'.format(args.config_file[0], e))
        sys.exit(1)

    try:
        process_date(dateutil.parser.parse(args.process_date[0]).date())
    except Exception as e:
        print('Failed to process data for {} ({})'.format(args.process_date[0], e))
        sys.exit(1)

if __name__ == "__main__":
    main()
