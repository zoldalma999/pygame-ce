"""Pygame module for loading and playing sounds.

This module contains classes for loading Sound objects and controlling
playback.

The mixer module has a limited number of channels for playback of sounds.
Usually programs tell pygame to start playing audio and it selects an available
channel automatically. The default is 8 simultaneous channels, but complex
programs can get more precise control over the number of channels and their
use.

All sound playback is mixed in background threads. When you begin to play a
Sound object, it will return immediately while the sound continues to play. A
single Sound object can also be actively played back multiple times.

The mixer also has a special streaming channel. This is for music playback and
is accessed through the :mod:`pygame.mixer.music` module. Consider using this
module for playing long running music. Unlike mixer module, the music module
streams the music from the files without loading music at once into memory.

The mixer module must be initialized like other pygame modules, but it has some
extra conditions. The ``pygame.mixer.init()`` function takes several optional
arguments to control the playback rate and sample size.

``NOTE``: For less laggy sound use a smaller buffer size. The default
is set to reduce the chance of scratchy sounds on some computers. You can
change the default buffer by calling :func:`pygame.mixer.pre_init` before
:func:`pygame.mixer.init` or :func:`pygame.init` is called. For example:
``pygame.mixer.pre_init(44100,-16,2, 1024)``

The following file formats are supported

   * ``WAV``

   * ``MP3``

   * ``OGG``

   * ``FLAC``

   * ``OPUS``

   * ``WV`` (WavPack)

   * ``MOD`` ("Module file" family of music file formats)

   * ``MIDI`` (see the :func:`get_soundfont` and :func:`set_soundfont` methods)

.. versionadded:: 2.5.0 Loading WV (Relies on SDL_mixer 2.8.0+)
"""

import sys
from typing import Any, Optional, Union, overload

from pygame.event import Event
from pygame.typing import FileLike
from typing_extensions import (
    Buffer,  # collections.abc 3.12
    deprecated,  # added in 3.13
)

from . import mixer_music

# export mixer_music as mixer.music
music = mixer_music

def init(
    frequency: int = 44100,
    size: int = -16,
    channels: int = 2,
    buffer: int = 512,
    devicename: Optional[str] = None,
    allowedchanges: int = 5,
) -> None:
    """Initialize the mixer module.

    Initialize the mixer module for Sound loading and playback. The default
    arguments can be overridden to provide specific audio mixing. Keyword
    arguments are accepted. For backwards compatibility, argument values of
    0 are replaced with the startup defaults, except for ``allowedchanges``,
    where -1 is used. (startup defaults may be changed by a :func:`pre_init` call).

    The size argument represents how many bits are used for each audio sample.
    If the value is negative then signed sample values will be used. Positive
    values mean unsigned audio samples will be used. An invalid value raises an
    exception.

    The channels argument is used to specify whether to use mono or stereo. 1
    for mono and 2 for stereo.
    ``NOTE``: The channels argument is not related to the number
    of channels for playback of sounds, that you can get with the function
    "get_num_channels" or set with the function "set_num_channels" (see below).

    The buffer argument controls the number of internal samples used in the
    sound mixer. The default value should work for most cases. It can be lowered
    to reduce latency, but sound dropout may occur. It can be raised to larger
    values to ensure playback never skips, but it will impose latency on sound
    playback. The buffer size must be a power of two (if not it is rounded up to
    the next nearest power of 2).

    The devicename parameter is the name of sound device to open for audio
    playback. Allowed device names will vary based on the host system.
    If left as ``None`` then a sensible default will be chosen for you.

    Some platforms require the :mod:`pygame.mixer` module to be initialized
    after the display modules have initialized. The top level ``pygame.init()``
    takes care of this automatically, but cannot pass any arguments to the mixer
    init. To solve this, mixer has a function ``pygame.mixer.pre_init()`` to set
    the proper defaults before the toplevel init is used.

    When using allowedchanges=0 it will convert the samples at runtime to match
    what the hardware supports. For example a sound card may not
    support 16bit sound samples, so instead it will use 8bit samples internally.
    If AUDIO_ALLOW_FORMAT_CHANGE is supplied, then the requested format will
    change to the closest that SDL supports.

    Apart from 0, allowedchanged accepts the following constants ORed together:

       - AUDIO_ALLOW_FREQUENCY_CHANGE
       - AUDIO_ALLOW_FORMAT_CHANGE
       - AUDIO_ALLOW_CHANNELS_CHANGE
       - AUDIO_ALLOW_ANY_CHANGE

    It is safe to call this more than once, but after the mixer is initialized
    you cannot change the playback arguments without first calling
    ``pygame.mixer.quit()``.

    .. versionchangedold:: 1.8 The default ``buffersize`` changed from 1024 to 3072.
    .. versionchangedold:: 1.9.1 The default ``buffersize`` changed from 3072 to 4096.
    .. versionchangedold:: 2.0.0 The default ``buffersize`` changed from 4096 to 512.
    .. versionchangedold:: 2.0.0 The default ``frequency`` changed from 22050 to 44100.
    .. versionchangedold:: 2.0.0 ``size`` can be 32 (32-bit floats).
    .. versionchangedold:: 2.0.0 ``channels`` can also be 4 or 6.
    .. versionaddedold:: 2.0.0 ``allowedchanges``, ``devicename`` arguments added
    """

def pre_init(
    frequency: int = 44100,
    size: int = -16,
    channels: int = 2,
    buffer: int = 512,
    devicename: Optional[str] = None,
    allowedchanges: int = 5,
) -> None:
    """Preset the mixer init arguments.

    Call pre_init to change the defaults used when the real
    ``pygame.mixer.init()`` is called. Keyword arguments are accepted. The best
    way to set custom mixer playback values is to call
    ``pygame.mixer.pre_init()`` before calling the top level ``pygame.init()``.
    For backwards compatibility, argument values of 0 are replaced with the
    startup defaults, except for ``allowedchanges``, where -1 is used.

    .. versionchangedold:: 1.8 The default ``buffersize`` changed from 1024 to 3072.
    .. versionchangedold:: 1.9.1 The default ``buffersize`` changed from 3072 to 4096.
    .. versionchangedold:: 2.0.0 The default ``buffersize`` changed from 4096 to 512.
    .. versionchangedold:: 2.0.0 The default ``frequency`` changed from 22050 to 44100.
    .. versionaddedold:: 2.0.0 ``allowedchanges``, ``devicename`` arguments added
    """

def quit() -> None:
    """Uninitialize the mixer.

    This will uninitialize :mod:`pygame.mixer`. All playback will stop and any
    loaded Sound objects may not be compatible with the mixer if it is
    reinitialized later.
    """

def get_init() -> tuple[int, int, int]:
    """Test if the mixer is initialized.

    If the mixer is initialized, this returns the playback arguments it is
    using. If the mixer has not been initialized this returns ``None``.
    """

def get_driver() -> str:
    """Get the name of the current audio backend driver.

    Pygame chooses one of many available audio backend drivers when it is
    initialized. This returns the internal name used for the backend. This
    function is intended to be used for getting diagnostic/debugging information.
    This can be controlled with ``SDL_AUDIODRIVER`` environment variable.

    .. versionadded:: 2.5.0
    """

def stop() -> None:
    """Stop playback of all sound channels.

    This will stop all playback of all active mixer channels.
    """

def pause() -> None:
    """Temporarily stop playback of all sound channels.

    This will temporarily stop all playback on the active mixer channels. The
    playback can later be resumed with ``pygame.mixer.unpause()``
    """

def unpause() -> None:
    """Resume paused playback of sound channels.

    This will resume all active sound channels after they have been paused.
    """

def fadeout(time: int, /) -> None:
    """Fade out the volume on all sounds before stopping.

    This will fade out the volume on all active channels over the time argument
    in milliseconds. After the sound is muted the playback will stop.
    """

def set_num_channels(count: int, /) -> None:
    """Set the total number of playback channels.

    Sets the number of available playback channels for the mixer. The default value is 8.
    The value can be increased or decreased. If the value is decreased, sounds
    playing on the truncated channels are stopped.
    """

def get_num_channels() -> int:
    """Get the total number of playback channels.

    Returns the number of currently active playback channels.
    """

def set_reserved(count: int, /) -> int:
    """Reserve channels from being automatically used.

    The mixer can reserve any number of channels that will not be automatically
    selected for playback by Sounds. This means that whenever you play a Sound
    without specifying a channel, a reserved channel will never be used. If sounds
    are currently playing on the reserved channels they will not be stopped.

    This allows the application to reserve a specific number of channels for
    important sounds that must not be dropped or have a guaranteed channel to
    play on.

    Will return number of channels actually reserved, this may be less than requested
    depending on the number of channels previously allocated.
    """

def find_channel(force: bool = False) -> Channel:
    """Find an unused channel.

    This will find and return an inactive Channel object. If there are no
    inactive Channels this function will return ``None``. If there are no
    inactive channels and the force argument is ``True``, this will find the
    Channel with the longest running Sound and return it.
    """

def set_soundfont(paths: Optional[str] = None, /) -> None:
    """Set the soundfont for playing midi music.

    This sets the soundfont file to be used in the playback of midi music.
    The soundfont only affects the playback of ``MID``, ``MIDI``, and ``KAR`` file formats.
    The optional ``path`` argument, a string (or multiple strings separated by a semi-colon),
    must point to the soundfont file(s) to be searched for in order given if some
    are missing. If ``path`` is an empty string or the default (``None``), any specified soundfont paths
    will be cleared from the mixer.

    Note on Windows, the mixer always uses the built-in soundfont instead of the one specified.

    Function :func:`set_soundfont` calls underlying SDL_mixer function
    ``Mix_SetSoundFonts``.

    .. versionadded:: 2.3.1
    """

def get_soundfont() -> Optional[str]:
    """Get the soundfont for playing midi music.

    This gets the soundfont filepaths as a string (each path is separated by a semi-colon)
    to be used in the playback of ``MID``, ``MIDI``, and ``KAR`` music file formats. If no
    soundfont is specified, the return type is ``None``.

    Function :func:`get_soundfont` calls underlying SDL_mixer function
    ``Mix_GetSoundFonts``.

    .. versionadded:: 2.3.1
    """

def get_busy() -> bool:
    """Test if any sound is being mixed.

    Returns ``True`` if the mixer is busy mixing any channels. If the mixer is
    idle then this return ``False``.
    """

def get_sdl_mixer_version(linked: bool = True) -> tuple[int, int, int]:
    """Get the mixer's SDL version.

    :param bool linked: if ``True`` (default) the linked version number is
       returned, otherwise the compiled version number is returned

    :returns: the mixer's SDL library version number (linked or compiled
       depending on the ``linked`` parameter) as a tuple of 3 integers
       ``(major, minor, patch)``
    :rtype: tuple

    .. note::
       The linked and compiled version numbers should be the same.

    .. versionaddedold:: 2.0.0
    """

class Sound:
    """Create a new Sound object from a file or buffer object.

    Load a new sound buffer from a filename, a python file object or a readable
    buffer object. Limited resampling will be performed to help the sample match
    the initialize arguments for the mixer. A Unicode string can only be a file
    pathname. A bytes object can be either a pathname or a buffer object.
    Use the 'file' or 'buffer' keywords to avoid ambiguity; otherwise Sound may
    guess wrong. If the array keyword is used, the object is expected to export
    a new buffer interface (The object is checked for a buffer interface first.)

    The Sound object represents actual sound sample data. Methods that change
    the state of the Sound object will the all instances of the Sound playback.
    A Sound object also exports a new buffer interface.

    The Sound can be loaded from an ``OGG`` audio file or from an uncompressed
    ``WAV``.

    Note: The buffer will be copied internally, no data will be shared between
    it and the Sound object.

    For now buffer and array support is consistent with ``sndarray.make_sound``
    for NumPy arrays, in that sample sign and byte order are ignored. This
    will change, either by correctly handling sign and byte order, or by raising
    an exception when different. Also, source samples are truncated to fit the
    audio sample size. This will not change.

    .. versionaddedold:: 1.8 ``pygame.mixer.Sound(buffer)``
    .. versionaddedold:: 1.9.2
       :class:`pygame.mixer.Sound` keyword arguments and array interface support
    .. versionaddedold:: 2.0.1 pathlib.Path support on Python 3.

    .. versionchanged:: 2.5.2 This class is also available through the ``pygame.Sound``
       alias.
    """

    @overload
    def __init__(self, file: FileLike) -> None: ...
    @overload
    def __init__(self, buffer: Buffer) -> None: ...
    # possibly going to be deprecated/removed soon, in which case these
    # typestubs must be removed too
    @property
    def __array_interface__(self) -> dict[str, Any]: ...
    @property
    def __array_struct__(self) -> Any: ...
    if sys.version_info >= (3, 12):
        def __buffer__(self, flags: int, /) -> memoryview[int]: ...
        def __release_buffer__(self, view: memoryview[int], /) -> None: ...
    def play(
        self,
        loops: int = 0,
        maxtime: int = 0,
        fade_ms: int = 0,
    ) -> Channel:
        """Begin sound playback.

        Begin playback of the Sound (i.e., on the computer's speakers) on an
        available Channel. This will forcibly select a Channel, so playback may
        cut off a currently playing sound if necessary.

        The loops argument controls how many times the sample will be repeated
        after being played the first time. A value of 5 means that the sound will
        be played once, then repeated five times, and so is played a total of six
        times. The default value (zero) means the Sound is not repeated, and so
        is only played once. If loops is set to -1 the Sound will loop
        indefinitely (though you can still call ``stop()`` to stop it).

        The maxtime argument can be used to stop playback after a given number of
        milliseconds.

        The fade_ms argument will make the sound start playing at 0 volume and
        fade up to full volume over the time given. The sample may end before the
        fade-in is complete.

        This returns the Channel object for the channel that was selected.
        """

    def stop(self) -> None:
        """Stop sound playback.

        This will stop the playback of this Sound on any active Channels.
        """

    def fadeout(self, time: int, /) -> None:
        """Stop sound playback after fading out.

        This will stop playback of the sound after fading it out over the time
        argument in milliseconds. The Sound will fade and stop on all actively
        playing channels.
        """

    def set_volume(self, value: float, /) -> None:
        """Set the playback volume for this Sound.

        This will set the playback volume (loudness) for this Sound. This will
        immediately affect the Sound if it is playing. It will also affect any
        future playback of this Sound.

        :param float value: volume in the range of 0.0 to 1.0 (inclusive)

           | If value < 0.0, the volume will not be changed
           | If value > 1.0, the volume will be set to 1.0

        .. note::
           The values are internally converted and kept as integer values in range [0, 128], which means
           that ``get_volume()`` may return a different volume than it was set to. For example,

              >>> sound.set_volume(0.1)
              >>> sound.get_volume()
              0.09375

           This is because when you ``set_volume(0.1)``, the volume is internally calculated like so

              >>> int(0.1 * 128)
              12

           This means that some of the precision is lost, so when you retrieve it again using ``get_volume()``,
           it is converted back to a ``float`` using that integer

              >>> 12 / 128
              0.09375
        """

    def get_volume(self) -> float:
        """Get the playback volume.

        Return a value from 0.0 to 1.0 (inclusive) representing the volume for this Sound.

        .. note::
           See :func:`Sound.set_volume` for more information regarding the returned value
        """

    def get_num_channels(self) -> int:
        """Count how many times this Sound is playing.

        Return the number of active channels this sound is playing on.
        """

    def get_length(self) -> float:
        """Get the length of the Sound.

        Return the length of this Sound in seconds.
        """

    def get_raw(self) -> bytes:
        """Return a bytestring copy of the Sound samples.

        Return a copy of the Sound object buffer as a bytes.

        .. versionaddedold:: 1.9.2
        """

class Channel:
    """Create a Channel object for controlling playback.

    Return a Channel object for one of the current channels. The id must be a
    value from 0 up to, but not including, ``pygame.mixer.get_num_channels()``.

    The Channel object can be used to get fine control over the playback of
    Sounds. A channel can only playback a single Sound at time. Using channels
    is entirely optional since pygame can manage them by default.

    .. versionchanged:: 2.1.4 This class is also available through the ``pygame.Channel``
       alias.
    .. versionchanged:: 2.4.0 It is now possible to create subclasses of ``pygame.mixer.Channel``
    """

    def __init__(self, id: int) -> None: ...
    @property
    def id(self) -> int:
        """Get the channel id for the Channel object.

        This simply returns the channel id used to create the ``Channel`` instance
        as a read-only attribute

        .. versionadded:: 2.4.0
        """

    def play(
        self,
        sound: Sound,
        loops: int = 0,
        maxtime: int = 0,
        fade_ms: int = 0,
    ) -> None:
        """Play a Sound on a specific Channel.

        This will begin playback of a Sound on a specific Channel. If the Channel
        is currently playing any other Sound it will be stopped.

        The loops argument has the same meaning as in ``Sound.play()``: it is the
        number of times to repeat the sound after the first time. If it is 3, the
        sound will be played 4 times (the first time, then three more). If loops
        is -1 then the playback will repeat indefinitely.

        As in ``Sound.play()``, the maxtime argument can be used to stop playback
        of the Sound after a given number of milliseconds.

        As in ``Sound.play()``, the fade_ms argument can be used fade in the
        sound.
        """

    def stop(self) -> None:
        """Stop playback on a Channel.

        Stop sound playback on a channel. After playback is stopped the channel
        becomes available for new Sounds to play on it.
        """

    def pause(self) -> None:
        """Temporarily stop playback of a channel.

        Temporarily stop the playback of sound on a channel. It can be resumed at
        a later time with ``Channel.unpause()``
        """

    def unpause(self) -> None:
        """Resume pause playback of a channel.

        Resume the playback on a paused channel.
        """

    def fadeout(self, time: int, /) -> None:
        """Stop playback after fading channel out.

        Stop playback of a channel after fading out the sound over the given time
        argument in milliseconds.
        """

    def set_source_location(self, angle: float, distance: float, /) -> None:
        """Set the position of a playing channel.

        Set the position (angle, distance) of a playing channel.

        `angle`: Angle is in degrees.

        `distance`: Range from 0 to 255.

        .. warning:: This function currently fails and raises a
            :exc:`pygame.error` when using 7.1 surround sound.
            By default, the mixer module will use what the hardware is best
            suited for, so this leads to hardware specific exceptions when using
            this function.

            One way of avoiding this is only using :func:`set_source_location`
            with forced stereo. For example

            ::

                pygame.mixer.pre_init(
                    channels=2,
                    allowedchanges=pygame.AUDIO_ALLOW_FREQUENCY_CHANGE,
                )
                pygame.init()

        .. versionadded:: 2.3.0
        """

    @overload
    def set_volume(self, value: float, /) -> None: ...
    @overload
    def set_volume(self, left: float, right: float, /) -> None: ...
    def set_volume(*args):  # type: ignore
        """Set the volume of a playing channel.

        Set the volume (loudness) of a playing sound. When a channel starts to
        play its volume value is reset. This only affects the current sound. The
        value argument is in the range of 0.0 to 1.0 (inclusive).

        If one argument is passed, it will be the volume of both speakers. If two
        arguments are passed and the mixer is in stereo mode, the first argument
        will be the volume of the left speaker and the second will be the volume
        of the right speaker. (If the second argument is ``None``, the first
        argument will be the volume of both speakers.)

        If the channel is playing a Sound on which ``set_volume()`` has also been
        called, both calls are taken into account. For example:

        ::

            sound = pygame.mixer.Sound("s.wav")
            channel = s.play()      # Sound plays at full volume by default
            sound.set_volume(0.9)   # Now plays at 90% of full volume.
            sound.set_volume(0.6)   # Now plays at 60% (previous value replaced).
            channel.set_volume(0.5) # Now plays at 30% (0.6 * 0.5).

        .. note::
           See :func:`Sound.set_volume` for more information regarding how the value is stored internally
        """

    def get_volume(self) -> float:
        """Get the volume of the playing channel.

        Return the volume of the channel for the current playing sound
        in the range of 0.0 to 1.0 (inclusive). This does
        not take into account stereo separation used by
        :meth:`Channel.set_volume`. The Sound object also has its own volume
        which is mixed with the channel.

        .. note::
           See :func:`Sound.set_volume` for more information regarding the returned value
        """

    def get_busy(self) -> bool:
        """Check if the channel is active.

        Returns ``True`` if the channel is actively mixing sound. If the channel
        is idle this returns ``False``.
        """

    def get_sound(self) -> Sound:
        """Get the currently playing Sound.

        Return the actual Sound object currently playing on this channel. If the
        channel is idle ``None`` is returned.
        """

    def queue(self, sound: Sound, /) -> None:
        """Queue a Sound object to follow the current.

        When a Sound is queued on a Channel, it will begin playing immediately
        after the current Sound is finished. Each channel can only have a single
        Sound queued at a time. The queued Sound will only play if the current
        playback finished automatically. It is cleared on any other call to
        ``Channel.stop()`` or ``Channel.play()``.

        If there is no sound actively playing on the Channel then the Sound will
        begin playing immediately.
        """

    def get_queue(self) -> Sound:
        """Return any Sound that is queued.

        If a Sound is already queued on this channel it will be returned. Once
        the queued sound begins playback it will no longer be on the queue.
        """

    def set_endevent(self, type: Union[int, Event] = 0, /) -> None:
        """Have the channel send an event when playback stops.

        When an endevent is set for a channel, it will send an event to the
        pygame queue every time a sound finishes playing on that channel (not
        just the first time). Use ``pygame.event.get()`` to retrieve the endevent
        once it's sent.

        Note that if you called ``Sound.play(n)`` or ``Channel.play(sound,n)``,
        the end event is sent only once: after the sound has been played "n+1"
        times (see the documentation of Sound.play).

        If ``Channel.stop()`` or ``Channel.play()`` is called while the sound was
        still playing, the event will be posted immediately.

        The type argument will be the event id sent to the queue. This can be any
        valid event type, but a good choice would be a value between
        ``pygame.locals.USEREVENT`` and ``pygame.locals.NUMEVENTS``. If no type
        argument is given then the Channel will stop sending endevents.
        """

    def get_endevent(self) -> int:
        """Get the event a channel sends when playback stops.

        Returns the event type to be sent every time the Channel finishes
        playback of a Sound. If there is no endevent the function returns
        ``pygame.NOEVENT``.
        """

@deprecated("Use `Sound` instead (SoundType is an old alias)")
class SoundType(Sound): ...

@deprecated("Use `Channel` instead (ChannelType is an old alias)")
class ChannelType(Channel): ...
