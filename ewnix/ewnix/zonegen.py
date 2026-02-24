import click
import ipaddress
from datetime import date
from jinja2 import Environment, PackageLoader
from urllib.parse import urlparse
import requests


#   Record and Zone classes

class Record:
    def __init__(self, name, value, rtype="A"):
        self.name = name
        self.value = value
        self.rtype = rtype

    def __repr__(self):
        return f"Record({self.name!r}, {self.value!r}, rtype={self.rtype!r})"


class Zone:
    def __init__(self, name):
        self.name = name.rstrip(".")
        self.ttls = {
            "refresh": 21600,
            "retry": 3600,
            "expire": 604800,
            "minimum": 86400,
        }
        self.records = []
        self.ns_records = []

    @property
    def serial(self):
        today = date.today().strftime("%Y%m%d")
        return f"{today}01"

    def add_ns(self, ns_name):
        self.ns_records.append(ns_name.rstrip("."))

    def add_record(self, name, value, rtype="A"):
        self.records.append(Record(name, value, rtype))


#   Main Click command

@click.command()
@click.option("-z", "--zone-name", required=True, help="DNS zone name")
@click.option(
    "-n",
    "--name-server",
    "name_servers",
    multiple=True,
    required=True,
    help="Nameserver hostname or FQDN (can be repeated)",
)
@click.option(
    "-s",
    "--subnet",
    required=True,
    help="Subnet in CIDR format, e.g. 10.200.12.0/22",
)
@click.option(
    "-f",
    "--output-file",
    type=click.Path(),
    default=None,
    help="Write output to a file instead of stdout",
)
@click.option(
    "-o",
    "--object-path",
    default=None,
    help="Object storage path: https://access:secret@host/bucket/zones/",
)
def command(zone_name, name_servers, subnet, output_file, object_path):
    """Generate a DNS zone file from a subnet and nameservers."""

    # Build Zone object
    zone = Zone(zone_name)

    # Add NS records
    for ns in name_servers:
        zone.add_ns(ns)

    # Parse subnet and generate host records
    network = ipaddress.ip_network(subnet, strict=False)
    for ip in network.hosts():
        octets = ip.exploded.split(".")
        third = format(int(octets[2]), "02x")
        fourth = format(int(octets[3]), "02x")
        hostname = f"host-{third}-{fourth}"
        zone.add_record(hostname, str(ip), rtype="A")

    # Sort records by hostname
    zone.records.sort(key=lambda r: r.name)

    # Render template
    env = Environment(loader=PackageLoader("ewnix", "templates"))
    template = env.get_template("zonefile.j2")
    output = template.render(zone=zone)

    # Write to file or stdout
    if output_file:
        with open(output_file, "w") as f:
            f.write(output)
    else:
        click.echo(output)

    # Bonus: upload to object storage if requested
    if object_path:
        upload_to_object_storage(object_path, zone.name, output)


#   Object storage upload

def upload_to_object_storage(object_path, zone_name, content):
    parsed = urlparse(object_path)

    auth = None
    if parsed.username and parsed.password:
        auth = (parsed.username, parsed.password)

    base = f"{parsed.scheme}://{parsed.hostname}"
    if parsed.port:
        base += f":{parsed.port}"

    path = parsed.path.rstrip("/")
    url = f"{base}{path}/{zone_name}.zone"

    resp = requests.put(url, data=content, auth=auth)
    resp.raise_for_status()
    click.echo(f"Uploaded zone file to {url}")
    
if __name__ == "__main__":
    command()