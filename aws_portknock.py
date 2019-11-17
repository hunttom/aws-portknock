#!/usr/bin/env python
import atexit
import boto3
import botocore.exceptions
import click
try:
    import configparser
except:
    import ConfigParser as configparser
import os
import sys
import time

if sys.version_info.major >= 3:
    # Python 3
    from urllib.request import urlopen
    python2 = False
else:
    # Python 2
    from urllib2 import urlopen
    python2 = True


def close_port(sgid, cidr_ip, port, protocol):
    ec2_client = boto3.client('ec2')
    ec2_client.revoke_security_group_ingress(
        GroupId=sgid,
        IpProtocol=protocol,
        CidrIp=cidr_ip,
        FromPort=port,
        ToPort=port
    )
    click.echo("Closed {} to {}; on protocol {}; on port {}".format(sgid, cidr_ip, protocol, port))


def get_ip():
    ip = urlopen('http://ip.42.pl/raw').read()
    if not python2:
        ip = ip.decode('utf-8')
    return "{}/32".format(ip)


def open_port(sgid, cidr_ip, port, protocol):
    ec2_client = boto3.client('ec2')
    ec2_client.authorize_security_group_ingress(
        GroupId=sgid,
        IpProtocol=protocol,
        CidrIp=cidr_ip,
        FromPort=port,
        ToPort=port
    )
    click.echo("Opened {} to {}; on protocol {}; on port {}".format(sgid, cidr_ip, protocol, port))


def keep_open(sgid, port, protocol):
    # check if we need to open port
    try:
        _cidr_ip = get_ip()
        open_port(sgid, _cidr_ip, port, protocol)
        # no exception means we added a new rule
        # so clean up afterwards
        atexit.register(close_port,
                        sgid=sgid,
                        cidr_ip=_cidr_ip,
                        protocol=protocol,
                        port=port)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'InvalidPermission.Duplicate':
            click.echo(e.response['Error']['Message'])
        else:
            raise e
    click.echo("Press CTRL-C when done.")
    while True:
        time.sleep(3600)


@click.command()
@click.option('-p', '--port', type=int, help='Port to open.')
@click.option('-r', '--profile', default='default',
              help='Configuration profile to use.')
@click.option('-t', '--protocol', type=str,
              help='Options: "tcp", "upd", "icmp"')
@click.option('-s', '--sgid', help='Security group ID.')

def cli(sgid, profile, port, protocol):
    config = configparser.ConfigParser()
    cfg_file = os.path.join(os.path.expanduser('~'),
                            '.aws',
                            'portknock.ini')
    if os.path.exists(cfg_file):
        config.read(cfg_file)
    if not sgid:
        if config.has_option(profile, 'sgid'):
            sgid = config.get(profile, 'sgid')
        else:
            click.echo("Cannot determine security group ID", err=True)
            sys.exit(1)
    if not port:
        if config.has_option(profile, 'port'):
            port = config.getint(profile, 'port')
        else:
            port = 22
    if not protocol:
        if config.has_option(profile, 'protocol'):
            protocol = config.get(profile, 'protocol')
        else:
            protocol = 'tcp'
    keep_open(sgid, port, protocol)


if __name__ == '__main__':
    cli()