import os
from itertools import chain

from ._compat import ExitStack
from .click import unstyle
from .io import AtomicSaver
from .logging import log
from .utils import comment, format_requirement, dedup


class OutputWriter(object):
    def __init__(self, src_files, dst_file, dry_run, emit_header, emit_index,
                 emit_trusted_host, annotate, generate_hashes,
                 default_index_url, index_urls, trusted_hosts, format_control,
                 allow_unsafe=False):
        self.src_files = src_files
        self.dst_file = dst_file
        self.dry_run = dry_run
        self.emit_header = emit_header
        self.emit_index = emit_index
        self.emit_trusted_host = emit_trusted_host
        self.annotate = annotate
        self.generate_hashes = generate_hashes
        self.default_index_url = default_index_url
        self.index_urls = index_urls
        self.trusted_hosts = trusted_hosts
        self.format_control = format_control
        self.allow_unsafe = allow_unsafe

    def _sort_key(self, ireq):
        return (not ireq.editable, str(ireq.req).lower())

    def write_header(self):
        if self.emit_header:
            yield comment('#')
            yield comment('# This file is autogenerated by Pip Requ')
            yield comment('# To update, run:')
            yield comment('#')
            params = []
            if not self.emit_index:
                params += ['--no-index']
            if not self.emit_trusted_host:
                params += ['--no-trusted-host']
            if not self.annotate:
                params += ['--no-annotate']
            if self.generate_hashes:
                params += ["--generate-hashes"]
            params += ['--output-file', self.dst_file]
            params += self.src_files
            yield comment('#    pip-requ compile {}'.format(' '.join(params)))
            yield comment('#')

    def write_index_options(self):
        if self.emit_index:
            for index, index_url in enumerate(dedup(self.index_urls)):
                if index_url.rstrip('/') == self.default_index_url:
                    continue
                flag = '--index-url' if index == 0 else '--extra-index-url'
                yield '{} {}'.format(flag, index_url)

    def write_trusted_hosts(self):
        if self.emit_trusted_host:
            for trusted_host in dedup(self.trusted_hosts):
                yield '--trusted-host {}'.format(trusted_host)

    def write_format_controls(self):
        for nb in dedup(self.format_control.no_binary):
            yield '--no-binary {}'.format(nb)
        for ob in dedup(self.format_control.only_binary):
            yield '--only-binary {}'.format(ob)

    def write_flags(self):
        emitted = False
        for line in chain(self.write_index_options(),
                          self.write_trusted_hosts(),
                          self.write_format_controls()):
            emitted = True
            yield line
        if emitted:
            yield ''

    def _iter_lines(self, results, reverse_dependencies, primary_packages, hashes):
        for line in self.write_header():
            yield line
        for line in self.write_flags():
            yield line

        UNSAFE_PACKAGES = {'setuptools', 'distribute', 'pip'}

        packages = set()
        unsafe_packages = set()
        ignored_packages = set()
        for r in results:
            if r.name in UNSAFE_PACKAGES:
                unsafe_packages.add(r)
            else:
                reverse = reverse_dependencies.get(r.name.lower())
                if reverse and all(name in UNSAFE_PACKAGES for name in reverse):
                    ignored_packages.add(r)
                else:
                    packages.add(r)

        packages = sorted(packages, key=self._sort_key)
        unsafe_packages = sorted(unsafe_packages, key=self._sort_key)
        ignored_packages = sorted(ignored_packages, key=self._sort_key)

        for ireq in packages:
            line = self._format_requirement(ireq, reverse_dependencies, primary_packages, hashes=hashes)
            yield line

        if unsafe_packages:
            yield ''
            yield comment('# The following packages are considered to be unsafe in a requirements file:')

            for ireq in unsafe_packages:
                line = self._format_requirement(
                    ireq, reverse_dependencies, primary_packages,
                    hashes=hashes if self.allow_unsafe else None,
                    include_specifier=self.allow_unsafe)
                if self.allow_unsafe:
                    yield line
                else:
                    yield comment('# ' + line)

        if ignored_packages:
            yield ''
            yield comment(
                '# The following packages are required only by packages'
                ' considered to be unsafe in a requirements file:')

            for ireq in ignored_packages:
                line = self._format_requirement(
                    ireq, reverse_dependencies, primary_packages,
                    hashes=hashes if self.allow_unsafe else None,
                    include_specifier=self.allow_unsafe)
                if self.allow_unsafe:
                    yield line
                else:
                    yield comment('# ' + line)

    def write(self, results, reverse_dependencies, primary_packages, hashes):
        with ExitStack() as stack:
            f = None
            if not self.dry_run:
                f = stack.enter_context(AtomicSaver(self.dst_file))

            for line in self._iter_lines(results, reverse_dependencies, primary_packages, hashes):
                log.info(line)
                if f:
                    f.write(unstyle(line).encode('utf-8'))
                    f.write(os.linesep.encode('utf-8'))

    def _format_requirement(self, ireq, reverse_dependencies, primary_packages, include_specifier=True, hashes=None):
        line = format_requirement(ireq, include_specifier=include_specifier)

        ireq_hashes = (hashes if hashes is not None else {}).get(ireq)
        if ireq_hashes:
            for hash_ in sorted(ireq_hashes):
                line += " \\\n    --hash={}".format(hash_)

        if not self.annotate or ireq.name in primary_packages:
            return line

        # Annotate what packages this package is required by
        required_by = reverse_dependencies.get(ireq.name.lower(), [])
        if required_by:
            annotation = ", ".join(sorted(required_by))
            line = "{:24}{}{}".format(
                line,
                " \\\n    " if ireq_hashes else "  ",
                comment("# via " + annotation))
        return line