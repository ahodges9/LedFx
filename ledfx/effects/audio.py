import time
import logging
import pyaudio
from ledfx.effects import Effect, smooth
import voluptuous as vol
import ledfx.effects.mel as mel
from ledfx.effects.math import ExpFilter, ease_array
from ledfx.events import GraphUpdateEvent
import ledfx.effects.math as math
from functools import lru_cache
import numpy as np
import collections
import aubio
from aubio import fvec, cvec, filterbank, float_type
from math import log

_LOGGER = logging.getLogger(__name__)

from collections import namedtuple
FrequencyRange = namedtuple('FrequencyRange','min,max')

FREQUENCY_RANGES = {
    'sub_bass': FrequencyRange(20, 60),
    'bass': FrequencyRange(60, 250),
    'low_midrange': FrequencyRange(250, 500),
    'midrange': FrequencyRange(500, 2000),
    'upper_midrange': FrequencyRange(2000, 4000),
    'presence': FrequencyRange(4000, 6000),
    'brilliance': FrequencyRange(6000, 20000),
}

FREQUENCY_RANGES_SIMPLE = {
    'low': FrequencyRange(20, 250),
    'mid': FrequencyRange(250, 4000),
    'high': FrequencyRange(4000, 24000),
}

MIN_MIDI = 21
MAX_MIDI = 108

class AudioInputSource(object):

    _audio = None
    _stream = None
    _callbacks = []
    _audioWindowSize = 4

    AUDIO_CONFIG_SCHEMA = vol.Schema({
        vol.Optional('sample_rate', default = 60): int,
        vol.Optional('mic_rate', default = 48000): int,
        vol.Optional('fft_size', default = 2048): int,
        vol.Optional('device_index', default = 0): int,
        vol.Optional('pre_emphasis', default = 0.2): float,
        vol.Optional('min_volume', default = -70.0): float
    }, extra=vol.ALLOW_EXTRA)

    def __init__(self, ledfx, config):
        self._config = self.AUDIO_CONFIG_SCHEMA(config)
        self._ledfx = ledfx
        self._volume = -90
        self._volume_filter = ExpFilter(-90, alpha_decay=0.01, alpha_rise=0.99)

    def activate(self):

        if self._audio is None:
            self._audio = pyaudio.PyAudio()

        # Setup a pre-emphasis filter to help balance the highs
        self.pre_emphasis = None
        if self._config['pre_emphasis']:
            self.pre_emphasis = aubio.digital_filter(3)
            self.pre_emphasis.set_biquad(1., -self._config['pre_emphasis'], 0, 0, 0)

        # Setup the phase vocoder to perform a windowed FFT
        self._phase_vocoder = aubio.pvoc(
            self._config['fft_size'], 
            self._config['mic_rate'] // self._config['sample_rate'])
        self._frequency_domain_null = aubio.cvec(self._config['fft_size'])
        self._frequency_domain = self._frequency_domain_null
        self._frequency_domain_x = np.linspace(0, self._config['mic_rate'], (self._config["fft_size"] // 2) + 1)

        # Enumerate all of the input devices and find the one matching the
        # configured device index
        _LOGGER.info("Audio Input Devices:")
        info = self._audio.get_host_api_info_by_index(0)
        for i in range(0, info.get('deviceCount')):
            if (self._audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                _LOGGER.info("  [{}] {}".format(i, self._audio.get_device_info_by_host_api_device_index(0, i).get('name')))

        # Open the audio stream and start processing the input
        self._stream = self._audio.open(
            input_device_index=self._config['device_index'],
            format=pyaudio.paFloat32,
            channels=1,
            rate=self._config['mic_rate'],
            input=True,
            frames_per_buffer = self._config['mic_rate'] // self._config['sample_rate'],
            stream_callback = self._audio_sample_callback)
        self._stream.start_stream()

        _LOGGER.info("Audio source opened.")

    def deactivate(self):
        self._stream.stop_stream()
        
        self._stream.close()
        self._stream = None
        self._rolling_window = None
        _LOGGER.info("Audio source closed.")

    def subscribe(self, callback):
        """Registers a callback with the input source"""
        self._callbacks.append(callback)

        if len(self._callbacks) == 1:
            self.activate()

    def unsubscribe(self, callback):
        """Unregisters a callback with the input source"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

        if len(self._callbacks) == 0:
            self.deactivate()

    def _audio_sample_callback(self, in_data, frame_count, time_info, status):
        """Callback for when a new audio sample is acquired"""
        self._raw_audio_sample = np.fromstring(in_data, dtype=np.float32)

        self.pre_process_audio()
        self._invalidate_caches()
        self._invoke_callbacks()

        return (self._raw_audio_sample, pyaudio.paContinue)

    def _invoke_callbacks(self):
        """Notifies all clients of the new data"""
        for callback in self._callbacks:
            callback()

    def _invalidate_caches(self):
        """Invalidates the necessary cache"""
        pass

    def pre_process_audio(self):
        """
        Pre-processing stage that will run on every sample, only
        core functionality that will be used for every audio effect
        should be done here. Everything else should be deferred until
        queried by an effect.
        """

        # Calculate the current volume for silence detection
        self._volume = aubio.db_spl(self._raw_audio_sample)
        self._volume_filter.update(self._volume)

        # Calculate the frequency domain from the filtered data and
        # force all zeros when below the volume threshold
        if self._volume_filter.value > self._config['min_volume']:
            self._processed_audio_sample = self._raw_audio_sample

            # Perform a pre-emphasis to balance the highs and lows
            if self.pre_emphasis:
                self._processed_audio_sample = self.pre_emphasis(self._raw_audio_sample)

            # Pass into the phase vocoder to get a windowed FFT
            self._frequency_domain = self._phase_vocoder(self._processed_audio_sample)
        else:
            self._frequency_domain = self._frequency_domain_null

        # Light up some notifications for developer mode
        if self._ledfx.dev_enabled():
            self._ledfx.events.fire_event(GraphUpdateEvent(
                'fft', self._frequency_domain.norm, self._frequency_domain_x))

    def audio_sample(self, raw = False):
        """Returns the raw audio sample"""
        if raw:
            return self._raw_audio_sample
        return self._processed_audio_sample

    def frequency_domain(self):
        return self._frequency_domain

    def volume(self, filtered = True):
        if filtered:
            return self._volume_filter.value
        return self._volume

class MelbankInputSource(AudioInputSource):

    CONFIG_SCHEMA = vol.Schema({
        vol.Optional('samples', default = 24): int,
        vol.Optional('min_frequency', default = 20): int,
        vol.Optional('max_frequency', default = 18000): int,
        vol.Optional('min_volume', default = -70.0): float,
        vol.Optional('min_volume_count', default = 20): int,
        vol.Optional('coeffs_type', default = "scott"): str
    }, extra=vol.ALLOW_EXTRA)

    def __init__(self, ledfx, config):
        config = self.CONFIG_SCHEMA(config)
        super().__init__(ledfx, config)
        self._initialize_melbank()
        self._initialize_octaves()

    def _invalidate_caches(self):
        """Invalidates the cache for all melbank related data"""
        super()._invalidate_caches()
        self.melbank.cache_clear()
        self.melbank_filtered.cache_clear()
        self.interpolated_melbank.cache_clear()

    def _initialize_melbank(self):
        """Initialize all the melbank related variables"""

        # Few difference coefficient types for experimentation
        if self._config['coeffs_type'] == 'triangle':
            melbank_mel = np.linspace(
                aubio.hztomel(self._config['min_frequency']),
                aubio.hztomel(self._config['max_frequency']),
                self._config['samples'] + 2)
            self.melbank_frequencies = np.array(
                [aubio.meltohz(mel) for mel in melbank_mel]).astype(np.float32)

            self.filterbank = aubio.filterbank(
                self._config['samples'],
                self._config['fft_size'])
            self.filterbank.set_triangle_bands(
                self.melbank_frequencies,
                self._config['mic_rate'])
            self.melbank_frequencies = self.melbank_frequencies[1:-1]

        if self._config['coeffs_type'] == 'bark':
            melbank_bark = np.linspace(
                6.0 * np.arcsinh(self._config['min_frequency'] / 600.0),
                6.0 * np.arcsinh(self._config['max_frequency'] / 600.0),
                self._config['samples'] + 2)
            self.melbank_frequencies = (600.0 * np.sinh(melbank_bark / 6.0)).astype(np.float32)

            self.filterbank = aubio.filterbank(
                self._config['samples'],
                self._config['fft_size'])
            self.filterbank.set_triangle_bands(
                self.melbank_frequencies,
                self._config['mic_rate'])
            self.melbank_frequencies = self.melbank_frequencies[1:-1]

        # Slaney coefficients will always produce 40 samples spanning 133Hz to 6000Hz
        if self._config['coeffs_type'] == 'slaney':
            self.filterbank = aubio.filterbank(40,
                self._config['fft_size'])
            self.filterbank.set_mel_coeffs_slaney(
                self._config['mic_rate'])

            # Sanley frequencies are linear-log spaced where 133Hz to 1000Hz is linear
            # spaced and 1000Hz to 6000Hz is log spaced. It also produced a hardcoded
            # 40 samples.
            lowestFrequency = 133.3
            linearSpacing = 66.6666666
            logSpacing = 1.0711703
            linearFilters = 13
            logFilters = 27
            linearSpacedFreqs = lowestFrequency + np.arange(0, linearFilters) * linearSpacing
            logSpacedFreqs = linearSpacedFreqs[-1] * np.power(logSpacing, np.arange(1, logFilters + 1))

            self._config['samples'] = 40
            self.melbank_frequencies = np.hstack((linearSpacedFreqs, logSpacedFreqs)).astype(np.float32)

        # Standard mel coefficients 
        if self._config['coeffs_type'] == 'mel':
            self.filterbank = aubio.filterbank(
                self._config['samples'],
                self._config['fft_size'])
            self.filterbank.set_mel_coeffs(
                self._config['mic_rate'],
                self._config['min_frequency'],
                self._config['max_frequency'])
            
            # Frequencies wil be linearly spaced in the mel scale
            melbank_mel = np.linspace(
                aubio.hztomel(self._config['min_frequency']),
                aubio.hztomel(self._config['max_frequency']),
                self._config['samples'])
            self.melbank_frequencies = np.array(
                [aubio.meltohz(mel) for mel in melbank_mel])

        # HTK mel coefficients
        if self._config['coeffs_type'] == 'htk':
            self.filterbank = aubio.filterbank(
                self._config['samples'],
                self._config['fft_size'])
            self.filterbank.set_mel_coeffs_htk(
                self._config['mic_rate'],
                self._config['min_frequency'],
                self._config['max_frequency'])

            # Frequencies wil be linearly spaced in the mel scale
            melbank_mel = np.linspace(
                aubio.hztomel(self._config['min_frequency']),
                aubio.hztomel(self._config['max_frequency']),
                self._config['samples'])
            self.melbank_frequencies = np.array(
                [aubio.meltohz(mel) for mel in melbank_mel])

        # Coefficients based on Scott's audio reactive led project
        if self._config['coeffs_type'] == 'scott':
            (melmat, center_frequencies_hz, freqs) = mel.compute_melmat(
                num_mel_bands=self._config['samples'],
                freq_min=self._config['min_frequency'],
                freq_max=self._config['max_frequency'],
                num_fft_bands=int(self._config['fft_size'] // 2) + 1,
                sample_rate=self._config['mic_rate'])
            self.filterbank = aubio.filterbank(
                self._config['samples'],
                self._config['fft_size'])
            self.filterbank.set_coeffs(melmat.astype(np.float32))
            self.melbank_frequencies = center_frequencies_hz

        # "Mel"-spacing based on Scott's audio reactive led project. This
        # should in theory be the same as the above, but there seems to be
        # slight differences. Leaving both for science!
        if self._config['coeffs_type'] == 'scott_mel':
            def hertz_to_scott(freq):
                return 3340.0 * log(1 + (freq / 250.0), 9)
            def scott_to_hertz(scott):
                return 250.0 * (9**(scott / 3340.0)) - 250.0

            melbank_scott = np.linspace(
                hertz_to_scott(self._config['min_frequency']),
                hertz_to_scott(self._config['max_frequency']),
                self._config['samples'] + 2)
            self.melbank_frequencies = np.array(
                [scott_to_hertz(scott) for scott in melbank_scott]).astype(np.float32)

            self.filterbank = aubio.filterbank(
                self._config['samples'],
                self._config['fft_size'])
            self.filterbank.set_triangle_bands(
                self.melbank_frequencies,
                self._config['mic_rate'])
            self.melbank_frequencies = self.melbank_frequencies[1:-1]

        self.melbank_frequencies = self.melbank_frequencies.astype(int)

        # Normalize the filterbank triangles to a consistent height, the
        # default coeffs (for types other than legacy) will be normalized
        # by the triangles area which results in an uneven melbank
        if self._config['coeffs_type'] != 'scott' and self._config['coeffs_type'] == 'scott_mel':
            coeffs = self.filterbank.get_coeffs()
            coeffs /= np.max(coeffs, axis=-1)[:, None]
            self.filterbank.set_coeffs(coeffs)

        # Find the indexes for each of the frequency ranges
        for i in range(0, len(self.melbank_frequencies) - 1):
            if self.melbank_frequencies[i] < FREQUENCY_RANGES_SIMPLE['low'].max:
                self.lows_index = i
            elif self.melbank_frequencies[i] < FREQUENCY_RANGES_SIMPLE['mid'].max:
                self.mids_index = i
            elif self.melbank_frequencies[i] < FREQUENCY_RANGES_SIMPLE['high'].max:
                self.highs_index = i

        # Build up some of the common filters
        self.mel_gain = ExpFilter(np.tile(1e-1, self._config['samples']), alpha_decay=0.01, alpha_rise=0.99)
        self.mel_smoothing = ExpFilter(np.tile(1e-1, self._config['samples']), alpha_decay=0.2, alpha_rise=0.99)
        self.common_filter = ExpFilter(alpha_decay = 0.99, alpha_rise = 0.01)

    def _initialize_octaves(self, 
                            n_notes=12*2,
                            n_average=10,
                            average_weighting_factor=1/10,
                            resolution=0.1,
                            easing_slope=4.5,
                            easing_lean=0.4,
                            max_clip=1.0,
                            freq_low=220,
                            freq_high=7040):
        """Initialise all the octave note detection variables
        int     n_notes:                    Number of notes (divisions) per octave (recommend multiple of 12)
        int     n_average:                  Number of frames to compute average from. More frames = less noise and stronger peaks, but slower response
        float   average_weighting_factor    Factor of exponent used for weighting fft input frames. Higher value = more weighting towards fresh sampled octaves
        float   resolution                  Number of divisions in height for octave data
        float   easing_slope                Sharpness of easing slope function applied to octave
        float   easing_lean                 Lean of easing slope
        float   max_clip                    Upper clipping value for octave data. Data rarely exceeds 0.5, usually around 0.2 max
        int     freq_low:                   Lower limit to use from fft
        int     freq_high:                  Upper limit to use from fft

        # Easing parameters shown on this graph
        # https://www.desmos.com/calculator/fjtcjdt2jy
        """

        self.n_notes = n_notes
        self.max_clip = max_clip
        self.resolution = resolution
        self.easing_slope = easing_slope
        self.easing_lean = easing_lean
        self.min_peak_height = min_peak_height
        self.min_peak_seperation = min_peak_seperation
        freq_range = np.array([freq_low, freq_high])
        # Linear scale of frequencies from 0 to MIC_RATE, with fft.norm.size number of values
        self.lin_scale = np.linspace(0, self._config['mic_rate'], self._config["fft_size"]//2+1)
        # limits converted to octaves above and below 440Hz (A). Non-integer octaves rounded down.
        octave_range = np.log2(440/freq_range).astype(int)
        # All octave frequencies ranging from lower to upper limit eg: [110, 220, 440, 880, 1760,  3520,  7040, 14080]
        log_scale = np.array([440/2**i for i in range(*octave_range,-1)]).astype(int)
        # Indexes of fft to use for each octave
        self.octave_indexes = np.searchsorted(self.lin_scale, log_scale)
        # 3d array where octaves are stored. Used to get an average over n_average samples
        self.rolling_octaves_stack = np.zeros((n_average, octave_range[0]-octave_range[1]-1, self.n_notes))
        # Weighting array for rolling average. More recent calculated octave (higher in stack) given more weight in octave average.
        self.average_weighting = np.exp(-average_weighting_factor*np.array(range(n_average)))
        # 1d array where the averaged octave data is stored.
        self.averaged_octave = np.zeros(self.n_notes)
        # 1d array where indexes of prominent notes in the octave are stored.
        self.notes = np.array([], dtype=np.float64)
        # Exp smoothing filter for output
        self.octave_smoothing = ExpFilter(np.tile(1e-1, self.n_notes), alpha_decay=0.6, alpha_rise=0.99)

    def octaves(self, fft):
        """Updates self.averaged_octave data"""

        octaves = np.split(fft.norm, self.octave_indexes)[1:-1]
        # Scale all octave arrays to be the length of the number of notes
        interpolated_octaves = []
        for octave in octaves:
            interpolated_octaves.append(np.interp(np.arange(0,len(octave), len(octave)/self.n_notes), np.arange(0, len(octave)), octave))
        interpolated_octaves = np.asarray(interpolated_octaves)
        # Roll the octaves stack alone by one to make room
        self.rolling_octaves_stack = np.roll(self.rolling_octaves_stack, 1, axis=0)
        # Add the freshly made octave data to the top of the stack
        self.rolling_octaves_stack[0] = interpolated_octaves
        # Calculate averages across octave, with newer octaves given more weight
        self.averaged_octave = np.average(self.rolling_octaves_stack.sum(axis=1), axis=0, weights=self.average_weighting)
        # Calculate the average height of octave peaks for cutoff
        average_cutoff = np.mean(self.averaged_octave)
        # Remove values below average
        self.averaged_octave -= average_cutoff
        # Clip between 0 and max_clip
        self.averaged_octave = np.clip(self.averaged_octave, 0, self.max_clip)
        # Scale between 0 and 1
        self.averaged_octave *= 1/self.max_clip
        #self.averaged_octave *= 2.0/self.max_clip
        #self.averaged_octave *= 2.0/self.averaged_octave.max()
        # Raise to amplification power
        # self.averaged_octave = np.power(self.averaged_octave, self.amplification_power)
        # Run octave through easing function to seperate lows from highs
        self.averaged_octave = ease_array(self.averaged_octave,
                                          height=1,
                                          length=1,
                                          slope=self.easing_slope,
                                          lean=self.easing_lean)
        # Smooth output using exp filter
        self.averaged_octave = self.octave_smoothing.update(self.averaged_octave)
        # Make octave values only multiples of resolution eg [0.0, 0.7, 0.5] rather than [0.0021, 0.73824, 0.5234]
        self.averaged_octave -= self.averaged_octave % self.resolution
        # Detect notes in octave data by looking for peaks. Data is padded with 0 either end to allow end cases to be detected as peaks.
        # self.notes is an array containing indexes of peaks.
        # self.notes = detect_peaks(np.pad(self.averaged_octave,
        #                                  (1,1),
        #                                  "constant",
        #                                  constant_values=(0)),
        #                           mph=self.min_peak_height,
        #                           mpd=self.min_peak_seperation,
        #                           threshold=0,
        #                           edge="rising") - 1 # -1 to remove pad from indexed values
        # print(len(self.notes), self.notes, len(self.averaged_octave))

    @lru_cache(maxsize=32)
    def melbank(self):
        """Returns the raw melbank curve"""
        if self.volume() > self._config['min_volume']:
            # Compute the filterbank from the frequency information
            raw_filter_banks = self.filterbank(self.frequency_domain())
            raw_filter_banks = raw_filter_banks ** 2.0
            self.mel_gain.update(np.max(smooth(raw_filter_banks, sigma=1.0)))
            filter_banks = raw_filter_banks / self.mel_gain.value
            filter_banks = self.mel_smoothing.update(filter_banks)
        else:
            raw_filter_banks = np.zeros(self._config['samples'])
            filter_banks = raw_filter_banks

        if self._ledfx.dev_enabled():
            self._ledfx.events.fire_event(GraphUpdateEvent(
                'raw', raw_filter_banks, np.array(self.melbank_frequencies)))
            self._ledfx.events.fire_event(GraphUpdateEvent(
                'melbank', filter_banks, np.array(self.melbank_frequencies)))
        return filter_banks

    def calc_octaves(self):
        self.octaves(self.frequency_domain())
        self._ledfx.events.fire_event(GraphUpdateEvent(
            'octave', self.averaged_octave*2.0, np.arange(self.n_notes)))

    def melbank_lows(self):
        return self.melbank()[:self.lows_index]

    def melbank_mids(self):
        return self.melbank()[self.lows_index+1:self.mids_index]

    def melbank_highs(self):
        return self.melbank()[self.highs_index:]

    @lru_cache(maxsize=32)
    def melbank_filtered(self):
        # TODO: Should probably account for the filtered melbank not being
        # queried every frame which would result in a poor filter. Need a 
        # good balance between wasting compute resources and quality filters.
        return self.common_filter.update(self.melbank())

    def sample_melbank(self, hz):
        """Samples the melbank curve at a given frequency"""
        return np.interp(hz, self.melbank_frequencies, self.melbank())

    @lru_cache(maxsize=32)
    def interpolated_melbank(self, size, filtered = True):
        """Returns a melbank curve interpolated up to a given size"""
        if filtered is True:
            return math.interpolate(self.melbank_filtered(), size)

        return math.interpolate(self.melbank(), size)

@Effect.no_registration
class AudioReactiveEffect(Effect):
    """
    Base for audio reactive effects. This really just subscribes
    to the melbank input source and forwards input along to the 
    subclasses. This can be expanded to do the common r/g/b filters.
    """

    def activate(self, channel):
        _LOGGER.info('Activating AudioReactiveEffect.')
        super().activate(channel)

        if not self._ledfx.audio or id(MelbankInputSource) != id(self._ledfx.audio.__class__):
            self._ledfx.audio = MelbankInputSource(self._ledfx, self._ledfx.config.get('audio', {}))

        self.audio = self._ledfx.audio
        self._ledfx.audio.subscribe(
            self._audio_data_updated)

    def deactivate(self):
        _LOGGER.info('Deactivating AudioReactiveEffect.')
        self.audio.unsubscribe(
            self._audio_data_updated)
        super().deactivate()

    def create_filter(self, alpha_decay, alpha_rise):
        # TODO: Since most effects reuse the same general filters it would be
        # nice for all that computation to be shared. This mean that shared
        # filters are needed, or if there is really just a small set of filters
        # that those get added to the Melbank input source instead.
        return ExpFilter(alpha_decay=alpha_decay, alpha_rise=alpha_rise)

    def _audio_data_updated(self):
        if self.is_active:
            self.audio_data_updated(self.audio)

    def audio_data_updated(self, data):  
        """
        Callback for when the audio data is updated. Should
        be implemented by subclasses
        """
        pass

    def _octave_data_updated(self):
        if self.is_active:
            self.octave_data_updated(get_melbank_input_source(self._ledfx))

    def octave_data_updated(self, data):
        """
        Callback for when the audio data is updated. Should
        be implemented by subclasses
        """
        pass
