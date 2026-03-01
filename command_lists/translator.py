import deepl as _deepl

import command_management.commands as _commands
import soup_util.constants as _constants
from . import _azure_translator


_deepl_translator = _deepl.Translator(_constants.DEEPL_API_KEY)

_AUTOCOMPLETE = {
    "from_language": _constants.AZURE_TRANSLATION_KEY.keys(),
    "to_language": _constants.AZURE_TRANSLATION_KEY.keys()
}


class CommandList(_commands.CommandList):

    name = "Translator"

    async def on_close(self):
        _deepl_translator.close()

    @_commands.command("translate",
                       desc="Translates some provided text to English. Can also give languages to translate to or from.",
                       autocomplete_fields=_AUTOCOMPLETE)
    async def translate_text(self, context, text: str, from_language: str = "auto", to_language: str = "english"):
        # if deepl does not have the language, azure is used as a backup
        # azure is used for automatic language detection

        if from_language.lower() not in _constants.AZURE_TRANSLATION_KEY and from_language.lower() != "auto":
            raise _commands.CommandError("Language to translate from is not available.")
        elif to_language.lower() not in _constants.AZURE_TRANSLATION_KEY:
            raise _commands.CommandError("Language to translate to is not available.")

        translator = "deepl"

        # from
        if from_language.lower() == "auto":
            source_lang = _azure_translator.detect(text)

            if source_lang is None:
                raise _commands.CommandError("Not able to detect the language.")
            elif source_lang.lower() not in [language_id.lower() for language_id in _constants.DEEPL_TRANSLATION_KEY["source"].values()]:
                translator = "azure"

        elif from_language.lower() in _constants.DEEPL_TRANSLATION_KEY["source"]:
            source_lang = _constants.DEEPL_TRANSLATION_KEY["source"][from_language.lower()]
        else:
            source_lang = _constants.AZURE_TRANSLATION_KEY[from_language.lower()]
            translator = "azure"

        # to
        if translator == "deepl" and to_language.lower() in _constants.DEEPL_TRANSLATION_KEY["target"]:
            target_lang = _constants.DEEPL_TRANSLATION_KEY["target"][to_language.lower()]
        else:
            target_lang = _constants.AZURE_TRANSLATION_KEY[to_language.lower()]

        # translate
        if translator == "deepl":
            translation = _deepl_translator.translate_text(text, source_lang=source_lang, target_lang=target_lang)
        else:
            translation = _azure_translator.translate(text, source_lang, target_lang)

        if translation is None:
            raise _commands.CommandError("An error occurred during the translation.")

        await context.send_message(translation)
