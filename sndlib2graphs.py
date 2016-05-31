#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2016
# Johannes K. Fichte, TU Wien, Austria
#
# sndlib2graphs is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.  sndlib2graphs is
# distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.  You should have received a copy of the
# GNU General Public License along with sndlib2graphs.  If not, see
# <http://www.gnu.org/licenses/>.

# Extract transport network graph from sndlib network problems

import logging
import optparse
import os
import sys
import StringIO

import xmltodict

from utils.graph import Graph

def options():
    usage = 'usage: %prog [options] file'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--output_file', dest='output_file', type='string',
                      help='Output file name [default: "./%type%/%file%.%type%"]', default=None)
    parser.add_option('--no_symtab', dest='symtab', action='store_false', default=True,
                      help='Do not output symtab [default: %default]')
    parser.add_option('--no_labels', dest='labels', action='store_false', default=True,
                      help='Do not output labels [default: %default]')
    parser.add_option('--stdout', dest='stdout', default=False,
                      help='Write output to stdout [default: %default]', action='store_true')
    parser.add_option('--output_type', dest='output_type', type='choice', choices=['gml', 'lp', 'gr', 'dimacs'],
                      help='Specifies the output type [default: %default]; allowed values: gml, lp, gr, dimacs',
                      default='gr')
    opts, files = parser.parse_args(sys.argv[1:])
    if len(files) < 1:
        logging.error('No files given %s.' % ','.join(files))
        print '*' * 80
        parser.print_help()
        exit(1)
    if len(files) > 2:
        logging.error('Too many files given. Only one file expected.')
        exit(1)
    path = os.path.realpath(files[0])
    if not opts.output_file:
        opts.output_file = '%s/%s/%s.%s' % (os.path.dirname(path), opts.output_type, os.path.basename(path), opts.output_type)
        directory = os.path.dirname(opts.output_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        logging.warning(
                'No outputfile given (by option --output_file) using default output file "%s"' % opts.output_file)
    return opts, path


def create_graph(doc):
    G = Graph()

    for node in doc['network']['networkStructure']['nodes']['node']:
        G.add_node(node['@id'], lat=node['coordinates']['x'], lon=node['coordinates']['y'])

    for edge in doc['network']['networkStructure']['links']['link']:
        modules = []
        try: 
            for _,v in edge['additionalModules'].iteritems():
                if isinstance(v,list):
                    for e in v:
                        m = {'capacity': e['capacity'], 'cost': e['cost']}
                        modules.append(m)
                else:
                    m = {'capacity': v['capacity'], 'cost': v['cost']}
                    modules.append(m)
        except KeyError:
            modules = []
        try:
            preInstalled=edge['preInstalledModule']
        except KeyError:
            preInstalled=''

        G.add_edge(edge['source'], edge['target'], preInstalledModule=preInstalled, additionalModules=modules)
    return G

def save_graph(G, output_file, stdout, gtfs_filename, output_type, symtab, labels):
    output = StringIO.StringIO()
    if output_type == 'gr':
        from utils.graph_output import write_gr as write_graph
        write_graph(G, symtab=symtab, labels=labels, output=output, gtfs_filename=gtfs_filename)
    elif output_type == 'dimacs':
        from utils.graph_output import write_dimacs as write_graph
        write_graph(G, symtab=symtab, labels=labels, output=output, gtfs_filename=gtfs_filename)
    elif output_type == 'lp':
        from utils.graph_output import write_lp as write_graph
        write_graph(G, symtab=symtab, labels=labels, output=output, gtfs_filename=gtfs_filename)
    elif output_type == 'gml':
        from utils.graph_output import write_gml as write_graph
        write_graph(G, symtab=symtab, labels=labels, output=output, gtfs_filename=gtfs_filename)
    else:
        logging.error('Output type (%s) not implemented' % opts.output_type)

    if not stdout:
        logging.warning('Writing output to file')
        with open(output_file, 'w') as f:
            f.write(output.getvalue())
            f.flush()
        logging.warning('Output written to: %s' % output_file)
    else:
        print output.getvalue()

if __name__ == '__main__':
    opts, path = options()
    with open(path) as fd:
        doc = xmltodict.parse(fd.read())

    G=create_graph(doc)
    save_graph(G, output_file=opts.output_file, stdout=opts.stdout, gtfs_filename=os.path.basename(path),output_type=opts.output_type, symtab=opts.symtab, labels=opts.labels)
