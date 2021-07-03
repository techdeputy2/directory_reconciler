from __future__ import print_function

import dns.resolver

class MailResolver:
    def __init__(self):
        self.dns_map = {}

    def check_email(self, email_address):
        parts = email_address.split('@')
        found = True

        if parts[1] not in self.dns_map.keys():
            try:
                dns.resolver.resolve(parts[1], 'MX')
                self.dns_map[parts[1]] = True
                found = True                
            except dns.resolver.NXDOMAIN:
                found = False
                pass
        return found
