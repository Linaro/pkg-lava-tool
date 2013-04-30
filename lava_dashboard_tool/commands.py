# Copyright (C) 2010,2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of lava-dashboard-tool.
#
# lava-dashboard-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-dashboard-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-dashboard-tool.  If not, see <http://www.gnu.org/licenses/>.

"""
Module with command-line tool commands that interact with the dashboard
server. All commands listed here should have counterparts in the
launch_control.dashboard_app.xml_rpc package.
"""

import argparse
import contextlib
import errno
import os
import re
import socket
import sys
import urllib
import urlparse
import xmlrpclib

import simplejson
from json_schema_validator.extensions import datetime_extension

from lava_tool.authtoken import AuthenticatingServerProxy, KeyringAuthBackend
from lava.tool.commands import ExperimentalCommandMixIn
from lava.tool.command import Command, CommandGroup


class dashboard(CommandGroup):
    """
    Commands for interacting with LAVA Dashboard
    """

    namespace = "lava.dashboard.commands"


class InsufficientServerVersion(Exception):
    """
    Exception raised when server version that a command interacts with is too
    old to support required features.
    """
    def __init__(self, server_version, required_version):
        self.server_version = server_version
        self.required_version = required_version


class DataSetRenderer(object):
    """
    Support class for rendering a table out of list of dictionaries.

    It supports several features that make printing tabular data easier.
    * Automatic layout
    * Custom column headers
    * Custom cell formatting
    * Custom table captions
    * Custom column ordering
    * Custom Column separators
    * Custom dataset notification

    The primary method is render() which does all of the above. You
    need to pass a dataset argument which is a list of dictionaries.
    Each dictionary must have the same keys. In particular the first row
    is used to determine columns.
    """
    def __init__(self, column_map=None, row_formatter=None, empty=None,
            order=None, caption=None, separator=" ", header_separator=None):
        if column_map is None:
            column_map = {}
        if row_formatter is None:
            row_formatter = {}
        if empty is None:
            empty = "There is no data to display"
        self.column_map = column_map
        self.row_formatter = row_formatter
        self.empty = empty
        self.order = order
        self.separator = separator
        self.caption = caption
        self.header_separator = header_separator

    def _analyze_dataset(self, dataset):
        """
        Determine the columns that will be displayed and the maximum
        length of each of those columns.

        Returns a tuple (dataset, columms, maxlen) where columns is a
        list of column names and maxlen is a dictionary mapping from
        column name to maximum length of any value in the row or the
        column header and the dataset is a copy of the dataset altered
        as necessary.

        Some examples:

        First the dataset, an array of dictionaries
        >>> dataset = [
        ...     {'a': 'shorter', 'bee': ''},
        ...     {'a': 'little longer', 'bee': 'b'}]

        Note that column 'bee' is actually three characters long as the
        column name made it wider.
        >>> dataset_out, columns, maxlen = DataSetRenderer(
        ...     )._analyze_dataset(dataset)

        Unless you format rows with a custom function the data is not altered.
        >>> dataset_out is dataset
        True

        Columns come out in sorted alphabetic order
        >>> columns
        ['a', 'bee']

        Maximum length determines the width of each column. Note that
        the header affects the column width.
        >>> maxlen
        {'a': 13, 'bee': 3}

        You can constrain or reorder columns. In that case columns you
        decided to ignore are simply left out of the output.
        >>> dataset_out, columns, maxlen = DataSetRenderer(
        ...     order=['bee'])._analyze_dataset(dataset)
        >>> columns
        ['bee']
        >>> maxlen
        {'bee': 3}

        You can format values anyway you like:
        >>> dataset_out, columns, maxlen = DataSetRenderer(row_formatter={
        ...     'bee': lambda value: "%10s" % value}
        ...     )._analyze_dataset(dataset)

        Dataset is altered to take account of the row formatting
        function. The original dataset argument is copied.
        >>> dataset_out
        [{'a': 'shorter', 'bee': '          '}, {'a': 'little longer', 'bee': '         b'}]
        >>> dataset_out is not dataset
        True

        Columns stay the same though:
        >>> columns
        ['a', 'bee']

        Note how formatting altered the width of the column 'bee'
        >>> maxlen
        {'a': 13, 'bee': 10}

        You can also format columns (with nice aliases).Note how
        column 'bee' maximum width is now dominated by the long column
        name:
        >>> dataset_out, columns, maxlen = DataSetRenderer(column_map={
        ...     'bee': "Column B"})._analyze_dataset(dataset)
        >>> maxlen
        {'a': 13, 'bee': 8}
        """
        if self.order:
            columns = self.order
        else:
            columns = sorted(dataset[0].keys())
        if self.row_formatter:
            dataset_out = [dict(row) for row in dataset]
        else:
            dataset_out = dataset
        for row in dataset_out:
            for column in row:
                if column in self.row_formatter:
                    row[column] = self.row_formatter[column](row[column])
        maxlen = dict(
                [(column, max(
                    len(self.column_map.get(column, column)),
                    max([
                        len(str(row[column])) for row in dataset_out])))
                    for column in columns])
        return dataset_out, columns, maxlen

    def _render_header(self, dataset, columns, maxlen):
        """
        Render a header, possibly with a caption string

        Caption is controlled by the constructor.
        >>> dataset = [
        ...     {'a': 'shorter', 'bee': ''},
        ...     {'a': 'little longer', 'bee': 'b'}]
        >>> columns = ['a', 'bee']
        >>> maxlen = {'a': 13, 'bee': 3}

        By default there is no caption, just column names:
        >>> DataSetRenderer()._render_header(
        ...     dataset, columns, maxlen)
              a       bee

        If you enable the header separator then column names will be visually
        separated from the first row of data.
        >>> DataSetRenderer(header_separator=True)._render_header(
        ...     dataset, columns, maxlen)
              a       bee
        -----------------

        If you provide a caption it gets rendered as a centered
        underlined text before the data:
        >>> DataSetRenderer(caption="Dataset")._render_header(
        ...     dataset, columns, maxlen)
             Dataset     
        =================
              a       bee

        You can use both caption and header separator
        >>> DataSetRenderer(caption="Dataset", header_separator=True)._render_header(
        ...     dataset, columns, maxlen)
             Dataset     
        =================
              a       bee
        -----------------

        Observe how the total length of the output horizontal line
        depends on the separator! Also note the columns labels are
        aligned to the center of the column
        >>> DataSetRenderer(caption="Dataset", separator=" | ")._render_header(
        ...     dataset, columns, maxlen)
              Dataset      
        ===================
              a       | bee
        """
        total_len = sum(maxlen.itervalues())
        if len(columns):
            total_len += len(self.separator) * (len(columns) - 1)
        # Print the caption
        if self.caption:
            print "{0:^{1}}".format(self.caption, total_len)
            print "=" * total_len
        # Now print the coulum names
        print self.separator.join([
            "{0:^{1}}".format(self.column_map.get(column, column),
                maxlen[column]) for column in columns])
        # Finally print the header separator
        if self.header_separator:
            print "-" * total_len

    def _render_rows(self, dataset, columns, maxlen):
        """
        Render rows of the dataset.

        Each row is printed on one line using the maxlen argument to
        determine correct column size. Text is aligned left.

        First the dataset, columns and maxlen as produced by
        _analyze_dataset()
        >>> dataset = [
        ...     {'a': 'shorter', 'bee': ''},
        ...     {'a': 'little longer', 'bee': 'b'}]
        >>> columns = ['a', 'bee']
        >>> maxlen = {'a': 13, 'bee': 3}

        Now a plain table. Note! To really understand this test
        you should check out the length of the strings below. There
        are two more spaces after 'b' in the second row
        >>> DataSetRenderer()._render_rows(dataset, columns, maxlen)
        shorter          
        little longer b  
        """
        for row in dataset:
            print self.separator.join([
                "{0!s:{1}}".format(row[column], maxlen[column])
                for column in columns])

    def _render_dataset(self, dataset):
        """
        Render the header followed by the rows of data.
        """
        dataset, columns, maxlen = self._analyze_dataset(dataset)
        self._render_header(dataset, columns, maxlen)
        self._render_rows(dataset, columns, maxlen)

    def _render_empty_dataset(self):
        """
        Render empty dataset.

        By default it just prints out a fixed sentence:
        >>> DataSetRenderer()._render_empty_dataset()
        There is no data to display

        This can be changed by passing an argument to the constructor
        >>> DataSetRenderer(empty="there is no data")._render_empty_dataset()
        there is no data
        """
        print self.empty

    def render(self, dataset):
        if len(dataset) > 0:
            self._render_dataset(dataset)
        else:
            self._render_empty_dataset()


class XMLRPCCommand(Command):
    """
    Abstract base class for commands that interact with dashboard server
    over XML-RPC.

    The only difference is that you should implement invoke_remote()
    instead of invoke(). The provided implementation catches several
    socket and XML-RPC errors and prints a pretty error message.
    """

    @staticmethod
    def _construct_xml_rpc_url(url):
        """
        Construct URL to the XML-RPC service out of the given URL
        """
        parts = urlparse.urlsplit(url)
        if not parts.path.endswith("/RPC2/"):
            path = parts.path.rstrip("/") + "/xml-rpc/"
        else:
            path = parts.path
        return urlparse.urlunsplit(
            (parts.scheme, parts.netloc, path, "", ""))

    @staticmethod
    def _strict_server_version(version):
        """
        Calculate strict server version (as defined by
        distutils.version.StrictVersion). This works by discarding .candidate
        and .dev release-levels.
        >>> XMLRPCCommand._strict_server_version("0.4.0.candidate.5")
        '0.4.0'
        >>> XMLRPCCommand._strict_server_version("0.4.0.dev.126")
        '0.4.0'
        >>> XMLRPCCommand._strict_server_version("0.4.0.alpha.1")
        '0.4.0a1'
        >>> XMLRPCCommand._strict_server_version("0.4.0.beta.2")
        '0.4.0b2'
        """
        try:
            major, minor, micro, releaselevel, serial = version.split(".") 
        except ValueError:
            raise ValueError(
                ("version %r does not follow pattern "
                 "'major.minor.micro.releaselevel.serial'") % version)
        if releaselevel in ["dev", "candidate", "final"]:
            return "%s.%s.%s" % (major, minor, micro)
        elif releaselevel == "alpha":
            return "%s.%s.%sa%s" % (major, minor, micro, serial)
        elif releaselevel == "beta":
            return "%s.%s.%sb%s" % (major, minor, micro, serial)
        else:
            raise ValueError(
                ("releaselevel %r is not one of 'final', 'alpha', 'beta', "
                 "'candidate' or 'final'") % releaselevel)

    def _check_server_version(self, server_obj, required_version):
        """
        Check that server object has is at least required_version.

        This method may raise InsufficientServerVersion.
        """
        from distutils.version import StrictVersion, LooseVersion
        # For backwards compatibility the server reports
        # major.minor.micro.releaselevel.serial which is not PEP-386 compliant
        server_version = StrictVersion(
            self._strict_server_version(server_obj.version()))
        required_version = StrictVersion(required_version)
        if server_version < required_version:
            raise InsufficientServerVersion(server_version, required_version)

    def __init__(self, parser, args):
        super(XMLRPCCommand, self).__init__(parser, args)
        xml_rpc_url = self._construct_xml_rpc_url(self.args.dashboard_url) 
        self.server = AuthenticatingServerProxy(
            xml_rpc_url,
            verbose=args.verbose_xml_rpc,
            allow_none=True,
            use_datetime=True,
            auth_backend=KeyringAuthBackend())

    def use_non_legacy_api_if_possible(self, name='server'):
        # Legacy APIs are registered in top-level object, non-legacy APIs are
        # prefixed with extension name.
        if "dashboard.version" in getattr(self, name).system.listMethods():
            setattr(self, name, getattr(self, name).dashboard)

    @classmethod
    def register_arguments(cls, parser):
        dashboard_group = parser.add_argument_group("dashboard specific arguments")
        default_dashboard_url = os.getenv("DASHBOARD_URL")
        if default_dashboard_url:
            dashboard_group.add_argument("--dashboard-url",
                    metavar="URL", help="URL of your validation dashboard (currently %(default)s)",
                    default=default_dashboard_url)
        else:
            dashboard_group.add_argument("--dashboard-url", required=True,
                    metavar="URL", help="URL of your validation dashboard")
        debug_group = parser.add_argument_group("debugging arguments")
        debug_group.add_argument("--verbose-xml-rpc",
                action="store_true", default=False,
                help="Show XML-RPC data")
        return dashboard_group

    @contextlib.contextmanager
    def safety_net(self):
        try:
            yield
        except socket.error as ex:
            print >> sys.stderr, "Unable to connect to server at %s" % (
                    self.args.dashboard_url,)
            # It seems that some errors are reported as -errno
            # while others as +errno.
            ex.errno = abs(ex.errno)
            if ex.errno == errno.ECONNREFUSED:
                print >> sys.stderr, "Connection was refused."
                parts = urlparse.urlsplit(self.args.dashboard_url)
                if parts.netloc == "localhost:8000":
                    print >> sys.stderr, "Perhaps the server is not running?"
            elif ex.errno == errno.ENOENT:
                print >> sys.stderr, "Unable to resolve address"
            else:
                print >> sys.stderr, "Socket %d: %s" % (ex.errno, ex.strerror)
        except xmlrpclib.ProtocolError as ex:
            print >> sys.stderr, "Unable to exchange XML-RPC message with dashboard server"
            print >> sys.stderr, "HTTP error code: %d/%s" % (ex.errcode, ex.errmsg)
        except xmlrpclib.Fault as ex:
            self.handle_xmlrpc_fault(ex.faultCode, ex.faultString)
        except InsufficientServerVersion as ex:
            print >> sys.stderr, ("This command requires at least server version "
                                 "%s, actual server version is %s" %
                                 (ex.required_version, ex.server_version))

    def invoke(self):
        with self.safety_net():
            self.use_non_legacy_api_if_possible()
            return self.invoke_remote()

    def handle_xmlrpc_fault(self, faultCode, faultString):
        if faultCode == 500:
            print >> sys.stderr, "Dashboard server has experienced internal error"
            print >> sys.stderr, faultString
        else:
            print >> sys.stderr, "XML-RPC error %d: %s" % (faultCode, faultString)

    def invoke_remote(self):
        raise NotImplementedError()


class server_version(XMLRPCCommand):
    """
    Display dashboard server version
    """

    def invoke_remote(self):
        print "Dashboard server version: %s" % (self.server.version(),)


class put(XMLRPCCommand):
    """
    Upload a bundle on the server
    """

    @classmethod
    def register_arguments(cls, parser):
        super(put, cls).register_arguments(parser)
        parser.add_argument("LOCAL",
                type=argparse.FileType("rb"),
                help="pathname on the local file system")
        parser.add_argument("REMOTE",
                default="/anonymous/", nargs='?',
                help="pathname on the server")

    def invoke_remote(self):
        content = self.args.LOCAL.read()
        filename = self.args.LOCAL.name
        pathname = self.args.REMOTE
        content_sha1 = self.server.put(content, filename, pathname)
        print "Stored as bundle {0}".format(content_sha1)

    def handle_xmlrpc_fault(self, faultCode, faultString):
        if faultCode == 404:
            print >> sys.stderr, "Bundle stream %s does not exist" % (
                    self.args.REMOTE)
        elif faultCode == 409:
            print >> sys.stderr, "You have already uploaded this bundle to the dashboard"
        else:
            super(put, self).handle_xmlrpc_fault(faultCode, faultString)


class get(XMLRPCCommand):
    """
    Download a bundle from the server
    """

    @classmethod
    def register_arguments(cls, parser):
        super(get, cls).register_arguments(parser)
        parser.add_argument("SHA1",
                type=str,
                help="SHA1 of the bundle to download")
        parser.add_argument("--overwrite",
                action="store_true",
                help="Overwrite files on the local disk")
        parser.add_argument("--output", "-o",
                type=argparse.FileType("wb"),
                default=None,
                help="Alternate name of the output file")

    def invoke_remote(self):
        response = self.server.get(self.args.SHA1)
        if self.args.output is None:
            filename = self.args.SHA1
            if os.path.exists(filename) and not self.args.overwrite:
                print >> sys.stderr, "File {filename!r} already exists".format(
                        filename=filename)
                print >> sys.stderr, "You may pass --overwrite to write over it"
                return -1
            stream = open(filename, "wb")
        else:
            stream = self.args.output
            filename = self.args.output.name
        stream.write(response['content'])
        print "Downloaded bundle {0} to file {1!r}".format(
                self.args.SHA1, filename)

    def handle_xmlrpc_fault(self, faultCode, faultString):
        if faultCode == 404:
            print >> sys.stderr, "Bundle {sha1} does not exist".format(
                    sha1=self.args.SHA1)
        else:
            super(get, self).handle_xmlrpc_fault(faultCode, faultString)


class deserialize(XMLRPCCommand):
    """
    Deserialize a bundle on the server
    """

    @classmethod
    def register_arguments(cls, parser):
        super(deserialize, cls).register_arguments(parser)
        parser.add_argument("SHA1",
                type=str,
                help="SHA1 of the bundle to deserialize")

    def invoke_remote(self):
        response = self.server.deserialize(self.args.SHA1)
        print "Bundle {sha1} deserialized".format(
            sha1=self.args.SHA1)

    def handle_xmlrpc_fault(self, faultCode, faultString):
        if faultCode == 404:
            print >> sys.stderr, "Bundle {sha1} does not exist".format(
                    sha1=self.args.SHA1)
        elif faultCode == 409:
            print >> sys.stderr, "Unable to deserialize bundle {sha1}".format(
                sha1=self.args.SHA1)
            print >> sys.stderr, faultString
        else:
            super(deserialize, self).handle_xmlrpc_fault(faultCode, faultString)


def _get_pretty_renderer(**kwargs):
    if "separator" not in kwargs:
        kwargs["separator"] = " | "
    if "header_separator" not in kwargs:
        kwargs["header_separator"] = True
    return DataSetRenderer(**kwargs)


class streams(XMLRPCCommand):
    """
    Show streams you have access to
    """

    renderer = _get_pretty_renderer(
        order=('pathname', 'bundle_count', 'name'),
        column_map={
            'pathname': 'Pathname',
            'bundle_count': 'Number of bundles',
            'name': 'Name'},
        row_formatter={
            'name': lambda name: name or "(not set)"},
        empty="There are no streams you can access on the server",
        caption="Bundle streams")

    def invoke_remote(self):
        self.renderer.render(self.server.streams())


class bundles(XMLRPCCommand):
    """
    Show bundles in the specified stream
    """

    renderer = _get_pretty_renderer(
            column_map={
                'uploaded_by': 'Uploader',
                'uploaded_on': 'Upload date',
                'content_filename': 'File name',
                'content_sha1': 'SHA1',
                'is_deserialized': "Deserialized?"},
            row_formatter={
                'is_deserialized': lambda x: "yes" if x else "no",
                'uploaded_by': lambda x: x or "(anonymous)",
                'uploaded_on': lambda x: x.strftime("%Y-%m-%d %H:%M:%S")},
            order=('content_sha1', 'content_filename', 'uploaded_by',
                'uploaded_on', 'is_deserialized'),
            empty="There are no bundles in this stream",
            caption="Bundles",
            separator=" | ")

    @classmethod
    def register_arguments(cls, parser):
        super(bundles, cls).register_arguments(parser)
        parser.add_argument("PATHNAME",
                default="/anonymous/", nargs='?',
                help="pathname on the server (defaults to %(default)s)")

    def invoke_remote(self):
        self.renderer.render(self.server.bundles(self.args.PATHNAME))

    def handle_xmlrpc_fault(self, faultCode, faultString):
        if faultCode == 404:
            print >> sys.stderr, "Bundle stream %s does not exist" % (
                    self.args.PATHNAME)
        else:
            super(bundles, self).handle_xmlrpc_fault(faultCode, faultString)


class make_stream(XMLRPCCommand):
    """
    Create a bundle stream on the server
    """

    @classmethod
    def register_arguments(cls, parser):
        super(make_stream, cls).register_arguments(parser)
        parser.add_argument(
            "pathname",
            type=str,
            help="Pathname of the bundle stream to create")
        parser.add_argument(
            "--name",
            type=str,
            default="",
            help="Name of the bundle stream (description)")

    def invoke_remote(self):
        self._check_server_version(self.server, "0.3")
        pathname = self.server.make_stream(self.args.pathname, self.args.name)
        print "Bundle stream {pathname} created".format(pathname=pathname)


class backup(XMLRPCCommand):
    """
    Backup data uploaded to a dashboard instance.
    
    Not all data is preserved. The following data is lost: identity of the user
    that uploaded each bundle, time of uploading and deserialization on the
    server, name of the bundle stream that contained the data
    """

    @classmethod
    def register_arguments(cls, parser):
        super(backup, cls).register_arguments(parser)
        parser.add_argument("BACKUP_DIR", type=str,
                            help="Directory to backup to")

    def invoke_remote(self):
        if not os.path.exists(self.args.BACKUP_DIR):
            os.mkdir(self.args.BACKUP_DIR)
        for bundle_stream in self.server.streams():
            print "Processing stream %s" % bundle_stream["pathname"]
            bundle_stream_dir = os.path.join(self.args.BACKUP_DIR, urllib.quote_plus(bundle_stream["pathname"]))
            if not os.path.exists(bundle_stream_dir):
                os.mkdir(bundle_stream_dir)
            with open(os.path.join(bundle_stream_dir, "metadata.json"), "wt") as stream:
                simplejson.dump({
                    "pathname": bundle_stream["pathname"],
                    "name": bundle_stream["name"],
                    "user": bundle_stream["user"],
                    "group": bundle_stream["group"],
                }, stream)
            for bundle in self.server.bundles(bundle_stream["pathname"]):
                print " * Backing up bundle %s" % bundle["content_sha1"]
                data = self.server.get(bundle["content_sha1"])
                bundle_pathname = os.path.join(bundle_stream_dir, bundle["content_sha1"]) 
                # Note: we write bundles as binary data to preserve anything the user might have dumped on us
                with open(bundle_pathname + ".json", "wb") as stream:
                    stream.write(data["content"])
                with open(bundle_pathname + ".metadata.json", "wt") as stream:
                    simplejson.dump({
                        "uploaded_by": bundle["uploaded_by"],
                        "uploaded_on": datetime_extension.to_json(bundle["uploaded_on"]),
                        "content_filename": bundle["content_filename"],
                        "content_sha1": bundle["content_sha1"],
                        "content_size": bundle["content_size"],
                    }, stream)


class restore(XMLRPCCommand):
    """
    Restore a dashboard instance from backup
    """

    @classmethod
    def register_arguments(cls, parser):
        super(restore, cls).register_arguments(parser)
        parser.add_argument("BACKUP_DIR", type=str,
                            help="Directory to backup from")

    def invoke_remote(self):
        self._check_server_version(self.server, "0.3")
        for stream_pathname_quoted in os.listdir(self.args.BACKUP_DIR):
            filesystem_stream_pathname = os.path.join(self.args.BACKUP_DIR, stream_pathname_quoted)
            if not os.path.isdir(filesystem_stream_pathname):
                continue
            stream_pathname = urllib.unquote(stream_pathname_quoted)
            if os.path.exists(os.path.join(filesystem_stream_pathname, "metadata.json")):
                with open(os.path.join(filesystem_stream_pathname, "metadata.json"), "rt") as stream:
                    stream_metadata = simplejson.load(stream)
            else:
                stream_metadata = {}
            print "Processing stream %s" % stream_pathname
            try:
                self.server.make_stream(stream_pathname, stream_metadata.get("name", "Restored from backup"))
            except xmlrpclib.Fault as ex:
                if ex.faultCode != 409:
                    raise
            for content_sha1 in [item[:-len(".json")] for item in os.listdir(filesystem_stream_pathname) if item.endswith(".json") and not item.endswith(".metadata.json") and item != "metadata.json"]:
                filesystem_content_filename = os.path.join(filesystem_stream_pathname, content_sha1 + ".json")
                if not os.path.isfile(filesystem_content_filename):
                    continue
                with open(os.path.join(filesystem_stream_pathname, content_sha1) + ".metadata.json", "rt") as stream:
                    bundle_metadata = simplejson.load(stream)
                with open(filesystem_content_filename, "rb") as stream:
                    content = stream.read()
                print " * Restoring bundle %s" % content_sha1
                try:
                    self.server.put(content, bundle_metadata["content_filename"], stream_pathname)
                except xmlrpclib.Fault as ex:
                    if ex.faultCode != 409:
                        raise
            

class pull(ExperimentalCommandMixIn, XMLRPCCommand):
    """
    Copy bundles and bundle streams from one dashboard to another.
    
    This command checks for two environment varialbes:
    The value of DASHBOARD_URL is used as a replacement for --dashbard-url.
    The value of REMOTE_DASHBOARD_URL as a replacement for FROM.
    Their presence automatically makes the corresponding argument optional.
    """

    def __init__(self, parser, args):
        super(pull, self).__init__(parser, args)
        remote_xml_rpc_url = self._construct_xml_rpc_url(self.args.FROM)
        self.remote_server = AuthenticatingServerProxy(
            remote_xml_rpc_url,
            verbose=args.verbose_xml_rpc,
            use_datetime=True,
            allow_none=True,
            auth_backend=KeyringAuthBackend())
        self.use_non_legacy_api_if_possible('remote_server')

    @classmethod
    def register_arguments(cls, parser):
        group = super(pull, cls).register_arguments(parser)
        default_remote_dashboard_url = os.getenv("REMOTE_DASHBOARD_URL")
        if default_remote_dashboard_url:
            group.add_argument(
                "FROM", nargs="?",
                help="URL of the remote validation dashboard (currently %(default)s)",
                default=default_remote_dashboard_url)
        else:
            group.add_argument(
                "FROM",
                help="URL of the remote validation dashboard)")
        group.add_argument("STREAM", nargs="*", help="Streams to pull from (all by default)")

    @staticmethod
    def _filesizeformat(num_bytes):
        """
        Formats the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
        102 num_bytes, etc).
        """
        try:
            num_bytes = float(num_bytes)
        except (TypeError, ValueError, UnicodeDecodeError):
            return "%(size)d byte", "%(size)d num_bytes" % {'size': 0}

        filesize_number_format = lambda value: "%0.2f" % (round(value, 1),)

        if num_bytes < 1024:
            return "%(size)d bytes" % {'size': num_bytes}
        if num_bytes < 1024 * 1024:
            return "%s KB" % filesize_number_format(num_bytes / 1024)
        if num_bytes < 1024 * 1024 * 1024:
            return "%s MB" % filesize_number_format(num_bytes / (1024 * 1024))
        return "%s GB" % filesize_number_format(num_bytes / (1024 * 1024 * 1024))

    def invoke_remote(self):
        self._check_server_version(self.server, "0.3")
        
        print "Checking local and remote streams"
        remote = self.remote_server.streams()
        if self.args.STREAM:
            # Check that all requested streams are available remotely
            requested_set = frozenset(self.args.STREAM)
            remote_set = frozenset((stream["pathname"] for stream in remote))
            unavailable_set = requested_set - remote_set
            if unavailable_set:
                print >> sys.stderr, "Remote stream not found: %s" % ", ".join(unavailable_set)
                return -1
            # Limit to requested streams if necessary
            remote = [stream for stream in remote if stream["pathname"] in requested_set]
        local = self.server.streams()
        missing_pathnames = set([stream["pathname"] for stream in remote]) - set([stream["pathname"] for stream in local])
        for stream in remote:
            if stream["pathname"] in missing_pathnames:
                self.server.make_stream(stream["pathname"], stream["name"])
                local_bundles = []
            else:
                local_bundles = [bundle for bundle in self.server.bundles(stream["pathname"])]
            remote_bundles = [bundle for bundle in self.remote_server.bundles(stream["pathname"])]
            missing_bundles = set((bundle["content_sha1"] for bundle in remote_bundles))
            missing_bundles -= set((bundle["content_sha1"] for bundle in local_bundles))
            try:
                missing_bytes = sum(
                    (bundle["content_size"]
                     for bundle in remote_bundles
                     if bundle["content_sha1"] in missing_bundles))
            except KeyError as ex:
                # Older servers did not return content_size so this part is optional
                missing_bytes = None
            if missing_bytes:
                print "Stream %s needs update (%s)" % (stream["pathname"], self._filesizeformat(missing_bytes))
            elif missing_bundles:
                print "Stream %s needs update (no estimate available)" % (stream["pathname"],)
            else:
                print "Stream %s is up to date" % (stream["pathname"],)
            for content_sha1 in missing_bundles:
                print "Getting %s" % (content_sha1,),
                sys.stdout.flush()
                data = self.remote_server.get(content_sha1)
                print "got %s, storing" % (self._filesizeformat(len(data["content"]))),
                sys.stdout.flush()
                try:
                    self.server.put(data["content"], data["content_filename"], stream["pathname"])
                except xmlrpclib.Fault as ex:
                    if ex.faultCode == 409:  # duplicate
                        print "already present (in another stream)"
                    else:
                        raise
                else:            
                    print "done"


class data_views(ExperimentalCommandMixIn, XMLRPCCommand):
    """
    Show data views defined on the server
    """
    renderer = _get_pretty_renderer(
        column_map={
            'name': 'Name',
            'summary': 'Summary',
        },
        order=('name', 'summary'),
        empty="There are no data views defined yet",
        caption="Data Views")

    def invoke_remote(self):
        self._check_server_version(self.server, "0.4")
        self.renderer.render(self.server.data_views())
        print
        print "Tip: to invoke a data view try `lc-tool query-data-view`"


class query_data_view(ExperimentalCommandMixIn, XMLRPCCommand):
    """
    Invoke a specified data view
    """
    @classmethod
    def register_arguments(cls, parser):
        super(query_data_view, cls).register_arguments(parser)
        parser.add_argument("QUERY", metavar="QUERY", nargs="...",
                           help="Data view name and any optional and required arguments")

    def _probe_data_views(self):
        """
        Probe the server for information about data views
        """
        with self.safety_net():
            self.use_non_legacy_api_if_possible()
            self._check_server_version(self.server, "0.4")
            return self.server.data_views()

    def reparse_arguments(self, parser, raw_args):
        self.data_views = self._probe_data_views()
        if self.data_views is None:
            return
        # Here we hack a little, the last actuin is the QUERY action added
        # in register_arguments above. By removing it we make the output
        # of lc-tool query-data-view NAME --help more consistent.
        del parser._actions[-1]
        subparsers = parser.add_subparsers(
            title="Data views available on the server")
        for data_view in self.data_views: 
            data_view_parser = subparsers.add_parser(
                data_view["name"],
                help=data_view["summary"],
                epilog=data_view["documentation"])
            data_view_parser.set_defaults(data_view=data_view)
            group = data_view_parser.add_argument_group("Data view parameters")
            for argument in data_view["arguments"]:
                if argument["default"] is None:
                    group.add_argument(
                        "--{name}".format(name=argument["name"].replace("_", "-")),
                        dest=argument["name"],
                        help=argument["help"],
                        type=str,
                        required=True)
                else:
                    group.add_argument(
                        "--{name}".format(name=argument["name"].replace("_", "-")),
                        dest=argument["name"],
                        help=argument["help"],
                        type=str,
                        default=argument["default"])
        self.args = self.parser.parse_args(raw_args)

    def invoke(self):
        # Override and _not_ call 'use_non_legacy_api_if_possible' as we
        # already did this reparse_arguments
        with self.safety_net():
            return self.invoke_remote()

    def invoke_remote(self):
        if self.data_views is None:
            return -1
        self._check_server_version(self.server, "0.4")
        # Build a collection of arguments for data view
        data_view_args = {}
        for argument in self.args.data_view["arguments"]:
            arg_name = argument["name"]
            if arg_name in self.args:
                data_view_args[arg_name] = getattr(self.args, arg_name) 
        # Invoke the data view
        response = self.server.query_data_view(self.args.data_view["name"], data_view_args) 
        # Create a pretty-printer
        renderer = _get_pretty_renderer(
            caption=self.args.data_view["summary"],
            order=[item["name"] for item in response["columns"]])
        # Post-process the data so that it fits the printer
        data_for_renderer = [
            dict(zip(
                [column["name"] for column in response["columns"]],
                row))
            for row in response["rows"]]
        # Print the data
        renderer.render(data_for_renderer)


class version(Command):
    """
    Show dashboard client version
    """
    def invoke(self):
        import versiontools
        from lava_dashboard_tool import __version__
        print "Dashboard client version: {version}".format(
            version=versiontools.format_version(__version__))
