# aws-portknock #
Port knocking for AWS security groups

## "Port knocking" ##

Unlike the traditional port knocking utilities, this tool relies on
the caller having the rights, through Amazon Web Services' Identity
and Access Management roles, to modify a security group.

## Requirements ##
1. Running the latest version of Python3.
2. Install necessary Python Libraries using `pip install -r requirements.txt`

## Usage ##

```
$ aws-portknock --help
Usage: aws-portknock [OPTIONS]

Options:
  -p, --port INTEGER  Port to open
  -r, --profile TEXT  Configuration profile to use
  -t, --protocol TEXT Protocol to use (tcp, udp, icmp)
  --sgid TEXT     Security group ID
  --help          Show this message and exit.
```

`aws-portknock` will determine the caller's public IP and add a rule
to the security group allowing access to the requested port from that
IP. It then sleeps until the user quits by using CTRL-C.

If a matching rule already exists, nothing happens on exit; otherwise,
that added rule is deleted when `aws-portknock` exits.

For repeated use, create `$HOME/.aws/portknock.ini` containing, for example:

```
[default]
sgid = sg-12abcdef
port = 22
protocol = tcp

[webprofile]
sgid = sg-12abcdef
port = 443
protocol = udp
```
