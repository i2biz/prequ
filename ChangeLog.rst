Unreleased
----------

- Allow pre-requirements without base requirements

0.300.0
-------

- Use ``[prequ]`` section in ``setup.cfg`` as default pre-requirements

0.200.1
-------

- (jazzband/pip-tools#464) sync: Use options from the txt file

0.200.0
-------

- Rename "prequ compile-all" to "prequ compile"
- (jazzband/pip-tools#427) Fix duplicate entries that could happen in
  generated requirements.txt
- (jazzband/pip-tools#457) Gracefully report invalid pip version
- (jazzband/pip-tools#452) Fix capitalization in the generated
  requirements.txt, packages will always be lowercased

0.180.9
-------

- (jazzband/pip-tools#453) Write relative find-links opts to output file
- Add "--silent" option for the compile command
- Rename "prequ compile" to "prequ compile-in"
- Use ``requirements.pre`` as input for ``prequ update``

0.180.8
-------

- Rename Pip Requ to Prequ

0.180.7
-------

- (jazzband/pip-tools#450) Calculated dependencies could be left with wrong
  candidates when toplevel requirements happen to be also pinned in
  sub-dependencies
- Convert README and ChangeLog to restructured text (ReST)
- Include README as package long description in setup.py

0.180.6
-------

- (jazzband/pip-tools#417) Exclude irrelevant pip constraints

0.180.5
-------

- Fix "pip-requ compile-all" to handle "-e" and "-c" lines correctly
- Remove "pip-compile" and "pip-sync" commands

0.180.4
-------

- Fix "pip-requ compile --no-annotate"

0.180.3
-------

- Add support for "pip-requ --version"

0.180.2
-------

- (jazzband/pip-tools#378) Recalculate secondary dependencies between rounds
- (jazzband/pip-tools#448) Add "--no-trusted-host" option to fix #382
- (jazzband/pip-tools#448) Deduplicate the option lines of output
- (jazzband/pip-tools#441) Exclude packages required only by unsafe packages
- (jazzband/pip-tools#389) Ignore pkg-resources
- (jazzband/pip-tools#355) Support non-editable pinned VCS dependencies

0.180.1
-------

- Add "pip-requ" command
- Add "pip-requ build-wheels" command
- Add "pip-requ compile-all" command
- Add "pip-requ update" command

0.180.0
-------

- Fork from pip-tools 1.8.0
