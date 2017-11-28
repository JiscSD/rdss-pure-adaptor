#!/usr/bin/env python3
import sys
import certifi


def main():
    new_cert_path = sys.argv[1]
    ca_file = certifi.where()
    print('Appending {} to {}.'.format(new_cert_path, ca_file))
    with open(new_cert_path, 'rb') as cert_in:
        new_certificate = cert_in.read()
    with open(ca_file, 'ab') as cert_out:
        cert_out.write(new_certificate)


if __name__ == '__main__':
    main()
