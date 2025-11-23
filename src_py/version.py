##    pygame - Python Game Library
##    Copyright (C) 2000-2003  Pete Shinners
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Library General Public
##    License as published by the Free Software Foundation; either
##    version 2 of the License, or (at your option) any later version.
##
##    This library is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##    Library General Public License for more details.
##
##    You should have received a copy of the GNU Library General Public
##    License along with this library; if not, write to the Free
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##    Pete Shinners
##    pete@shinners.org

"""Pygame module containing version information.

This module is automatically imported into the pygame package and can be used to
check which version of pygame has been imported.
"""

from pygame.base import __version__, get_sdl_version


class SoftwareVersion(tuple):
    """
    A class for storing data about software versions.
    """

    __slots__ = ()
    fields = "major", "minor", "patch"

    def __new__(cls, major, minor, patch):
        return tuple.__new__(cls, (major, minor, patch))

    def __repr__(self):
        fields = (f"{fld}={val}" for fld, val in zip(self.fields, self))
        return f"{str(self.__class__.__name__)}({', '.join(fields)})"

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    major = property(lambda self: self[0])
    minor = property(lambda self: self[1])
    patch = property(lambda self: self[2])


class PygameVersion(SoftwareVersion):
    """
    Pygame Version class.
    """


class SDLVersion(SoftwareVersion):
    """
    SDL Version class.
    """


_sdl_tuple = get_sdl_version()
SDL = SDLVersion(_sdl_tuple[0], _sdl_tuple[1], _sdl_tuple[2])
"""Tupled integers of the SDL library version.

This is the SDL library version represented as an extended tuple. It also has
attributes 'major', 'minor' & 'patch' that can be accessed like this:

::

    >>> pygame.version.SDL.major
    2

printing the whole thing returns a string like this:

::

    >>> pygame.version.SDL
    SDLVersion(major=2, minor=26, patch=5)

.. versionaddedold:: 2.0.0
"""

ver = __version__  # pylint: disable=invalid-name
"""Version number as a string.

This is the version represented as a string. It can contain a micro release
number as well, e.g. ``'1.5.2'``.
"""

vernum = PygameVersion(*map(int, ver.split(".")[:3]))
"""Tupled integers of the version.

This version information can easily be compared with other version
numbers of the same format. An example of checking pygame version numbers
would look like this:

::

    if pygame.version.vernum < (1, 5):
        print('Warning, older version of pygame (%s)' %  pygame.version.ver)
        disable_advanced_features = True

.. versionaddedold:: 1.9.6 Attributes ``major``, ``minor``, and ``patch``.

::

    vernum.major == vernum[0]
    vernum.minor == vernum[1]
    vernum.patch == vernum[2]

.. versionchangedold:: 1.9.6
    ``str(pygame.version.vernum)`` returns a string like ``"2.0.0"`` instead
    of ``"(2, 0, 0)"``.

.. versionchangedold:: 1.9.6
    ``repr(pygame.version.vernum)`` returns a string like
    ``"PygameVersion(major=2, minor=0, patch=0)"`` instead of ``"(2, 0, 0)"``.
"""

rev = ""  # pylint: disable=invalid-name
"""Repository revision of the build.

The Mercurial node identifier of the repository checkout from which this
package was built. If the identifier ends with a plus sign '+' then the
package contains uncommitted changes. Please include this revision number
in bug reports, especially for non-release pygame builds.

Important note: pygame development has moved to github, this variable is
obsolete now. As soon as development shifted to github, this variable started
returning an empty string ``""``.
It has always been returning an empty string since ``v1.9.5``.

.. versionchangedold:: 1.9.5
    Always returns an empty string ``""``.
"""

__all__ = ["SDL", "ver", "vernum", "rev"]
