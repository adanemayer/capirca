#!/usr/bin/env python
#
# this is the beginnings of the tool which will render policy
# files into usable iptables tables, cisco access lists or
# juniper firewall filters.

# system imports
from optparse import OptionParser
import os

# compiler imports
from lib import naming
from lib import policy

# renderer imports
from lib import cisco
from lib import iptables
from lib import juniper

output_policy_dict = {}

def render_policy(pol, input_file, output_directory):
  output_dir = os.path.join(os.path.dirname(os.path.dirname(input_file)),
                            output_directory)
  f = '%s%s' % (os.path.basename(input_file).split('.')[0], pol.suffix)
  output_file = os.path.join(output_dir, f)
  print output_file

  if output_file in output_policy_dict:
    output_policy_dict[output_file] += str(pol)
  else:
    output_policy_dict[output_file] = str(pol)

def output_policies():
  for output_file in output_policy_dict:
    output = open(output_file, 'w')
    if output:
      output.write(output_policy_dict[output_file])

def main(options):
  # first, load our naming
  if not options.definitions:
    return
  defs = naming.Naming(options.definitions)
  if not defs:
    print 'problem loading definitions'
    return
  
  # now, let's open our policy file
  if not options.policy:
    return
  pol = policy.ParsePolicy(open(options.policy).read(), defs)

  for header in pol.headers:
    if 'juniper' in header.platforms:
      print 'rendering juniper'
      render_policy(juniper.Juniper(pol), options.policy,
                    options.output_directory)

    if 'itpables' in header.platforms:
      print 'rendering iptables'
      render_policy(iptables.Iptables(pol), options.policy,
                    options.output_directory)

    if 'cisco' in header.platforms:
      print 'rendering cisco'
      render_policy(cisco.Cisco(pol), options.policy,
                    options.output_directory)

    output_policies()

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option('-d', '--def', dest='definitions',
                    help='defintions directory')
  parser.add_option('-o', '--output_directory', dest='output_directory',
                    default='filter', help='output directory')
  parser.add_option('-p', '--pol', dest='policy', help='policy file')
  parser.add_option('', '--poldir', dest='policies', help='policy directory')
  (options, args ) = parser.parse_args()
  
  main(options)