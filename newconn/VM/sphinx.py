########################################################
# Adapted from the SpeechRecognition (3.5.0) by Uberi
# https://github.com/Uberi/speech_recognition
########################################################

import os
import tempfile, shutil
 
   
class RequestError(Exception): pass

try:
	from pocketsphinx import pocketsphinx
	from sphinxbase import sphinxbase
except ImportError:
	raise RequestError("missing PocketSphinx module:\
	 ensure that PocketSphinx is set up correctly.")
except ValueError:
	raise RequestError("bad PocketSphinx installation detected;\
	 make sure you have PocketSphinx version 0.0.9 or better.")




class tempfile_TemporaryDirectory(object):
    """Python 2 compatibility: backport of ``tempfile.TemporaryDirectory``
    from Python 3"""

    def __enter__(self):
        self.name = tempfile.mkdtemp()
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.name)


class Sphinx():
	"""
		Performs speech recognition on raw audio data, using CMU Sphinx.

		The recognition language is determined by ``language``, an RFC5646
		language tag like ``"en-US"`` or ``"en-GB"``, defaulting to US English.
		Out of the box, only ``en-US`` is supported.

	"""

	def __init__(self, language = "en-US"):
		"""[summary]
		
		[description]
		
		Keyword Arguments:
			language {str} -- [description] (default: {"en-US"})
		
		Raises:
			RequestError -- There are issues with the Sphinx installation.
		"""
		assert isinstance(language, str), "``language`` must be a string"

		language_directory = os.path.join(os.path.dirname(
			os.path.realpath(__file__)), "pocketsphinx-data", language)

		if not os.path.isdir(language_directory):
			raise RequestError("missing PocketSphinx language data directory:\
			 \"{0}\"".format(language_directory))

		acoustic_parameters_directory = os.path.join(language_directory, 
			"acoustic-model")

		if not os.path.isdir(acoustic_parameters_directory):
			raise RequestError("missing PocketSphinx language model parameters\
			 directory: \"{0}\"".format(acoustic_parameters_directory))
		
		language_model_file = os.path.join(language_directory, 
			"language-model.lm.bin")

		if not os.path.isfile(language_model_file):
			raise RequestError("missing PocketSphinx language model file:\
			 \"{0}\"".format(language_model_file))
		
		phoneme_dictionary_file = os.path.join(language_directory,
		 "pronounciation-dictionary.dict")

		if not os.path.isfile(phoneme_dictionary_file):
			raise RequestError("missing PocketSphinx phoneme dictionary file:\
			 \"{0}\"".format(phoneme_dictionary_file))

		# create decoder object
		config = pocketsphinx.Decoder.default_config()
		
		# set the path of the hidden Markov model (HMM) parameter files
		config.set_string("-hmm", acoustic_parameters_directory)
		
		config.set_string("-lm", language_model_file)
		config.set_string("-dict", phoneme_dictionary_file)

		# disable logging (logging causes unwanted output in terminal)
		config.set_string("-logfn", os.devnull)

		self.decoder = pocketsphinx.Decoder(config)


	def recognize(self, raw_data, keyword_entries = None, show_all = False):
		"""Performs speech to text recognition using CMU Sphinx
		
		It's possible to search for specific keywords in the speech.
		If specified, the keywords to search for are determined by
		``keyword_entries``, an iterable of tuples of the form
		``(keyword, sensitivity)``, where ``keyword`` is a phrase, and
		``sensitivity`` is how sensitive to this phrase the recognizer
		should be, on a scale of 0 (very insensitive, more false negatives)
		to 1 (very sensitive, more false positives) inclusive.
		If not specified or ``None``, no keywords are used and Sphinx will
		simply transcribe whatever words it recognizes.
		Specifying ``keyword_entries`` is more accurate than just looking for
		those same keywords in non-keyword-based transcriptions,
		because Sphinx knows specifically what sounds to look for.
		
		Arguments:
			raw_data {[type]} -- Raw audio data to be recognized
		
		Keyword Arguments:
			keyword_entries {[type]} -- Keywords to search for (default: {None})
			show_all {bool} -- Sets the return to the most likely transcription
				if false, otherwise returns the Sphinx 
				``pocketsphinx.pocketsphinx.Decoder`` object resulting from the
				recognition. (default: {False})
		
		Raises:
			UnknownValueError -- The speech is unintelligible
		"""
		
		
		assert keyword_entries is None or all(isinstance(keyword, str) \
			and 0 <= sensitivity <= 1 \
			for keyword, sensitivity in keyword_entries),\
			 "``keyword_entries`` must be ``None`` or a list of pairs of\
			  strings and numbers between 0 and 1"

		
		# obtain recognition results
		if keyword_entries is not None: # explicitly specified set of keywords
			with tempfile_TemporaryDirectory() as temp_directory:
				# generate a keywords file - Sphinx documentation recommendeds
				# sensitivities between 1e-50 and 1e-5
				keywords_path = os.path.join(temp_directory, "keyphrases.txt")
				
				with open(keywords_path, "w") as f:
					f.writelines("{} /1e{}/\n"
						.format(keyword, 45 * sensitivity - 50) 
						for keyword, sensitivity in keyword_entries)

				# perform the speech recognition with the keywords file
				# (this is inside the context manager so the file isn't
				# deleted until we're done)
				self.decoder.set_kws("keywords", keywords_path)

				self.decoder.set_search("keywords")

				# begin utterance processing
				self.decoder.start_utt() 
				
				# process audio data with recognition enabled
				# (no_search = False), as a full utterance (full_utt = True)
				self.decoder.process_raw(raw_data, False, True)
				
				# stop utterance processing
				self.decoder.end_utt() 

		else: # no keywords, perform freeform recognition
			self.decoder.start_utt() # begin utterance processing
			
			# process audio data with recognition enabled (no_search = False),
			# as a full utterance (full_utt = True)
			self.decoder.process_raw(raw_data, False, True) 
			
			self.decoder.end_utt() # stop utterance processing

		if show_all: return self.decoder

		# return results
		hypothesis = self.decoder.hyp()
		if hypothesis is not None: return hypothesis.hypstr
		raise UnknownValueError() # no transcriptions available
