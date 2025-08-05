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

    name = "translator commands"

    async def on_start(self):
        pass

    async def on_close(self):
        _deepl_translator.close()

    @_commands.command("translate",
                       desc="Translates some provided text. Can optionally supply languages to translate to or from",
                       autocomplete_fields=_AUTOCOMPLETE)
    async def translate_text(self, context, text: str, from_language: str = "auto", to_language: str = "english"):
        # deepl has better translations, but has bad auto-detection and worse coverage than azure
        # this method uses azure for detection and deepl for translations
        # if deepl does not have the language, azure is used as a backup

        if to_language.lower() not in _constants.DEEPL_TRANSLATION_KEY["target"].keys() \
                or (from_language.lower() != "auto" and from_language.lower() not in _constants.DEEPL_TRANSLATION_KEY["source"].keys()):
            await context.send_message(_azure_translator.translate(text, from_language, to_language, ))
            return

        if from_language == "auto":
            source_lang = _azure_translator.detect(text)

            if source_lang is None:
                await context.send_message("not able to generate a translation")
                return
            elif source_lang not in _constants.DEEPL_TRANSLATION_KEY["source"].values():
                await context.send_message(_azure_translator.translate(text, from_language, to_language))
                return

        else:
            source_lang = _constants.DEEPL_TRANSLATION_KEY["source"][from_language.lower()]

        await context.send_message(_deepl_translator.translate_text(
            text,
            source_lang=source_lang,
            target_lang=_constants.DEEPL_TRANSLATION_KEY["target"][to_language.lower()]
        ))
