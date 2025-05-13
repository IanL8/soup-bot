import deepl

from command_management import commands
from soup_util.constants import  DEEPL_API_KEY, DEEPL_TRANSLATION_KEY, AZURE_TRANSLATION_KEY

from ._azure_translator import azure_translate, azure_detect


deepl_translator = deepl.Translator(DEEPL_API_KEY)


class CommandList(commands.CommandList):

    name = "translator commands"

    def on_close(self):
        deepl_translator.close()

    @commands.command("translate",
                      desc="Translates some provided text. Can optionally supply languages to translate to or from",
                      autocomplete_fields={"from_language": AZURE_TRANSLATION_KEY.keys(),
                                           "to_language": AZURE_TRANSLATION_KEY.keys()}
                      )
    async def translate_text(self, context, text: str, from_language: str = "auto", to_language: str = "english"):
        # deepl has better translations, but has bad auto-detection and worse coverage than azure
        # this method uses azure for detection and deepl for translations
        # if deepl does not have the language, azure is used as a backup

        if to_language.lower() not in DEEPL_TRANSLATION_KEY["target"].keys() \
                or (from_language.lower() != "auto" and from_language.lower() not in DEEPL_TRANSLATION_KEY[
            "source"].keys()):
            await context.send_message(azure_translate(text, from_language, to_language, ))
            return

        if from_language == "auto":
            source_lang = azure_detect(text)

            if source_lang is None:
                await context.send_message("not able to generate a translation")
                return
            elif source_lang not in DEEPL_TRANSLATION_KEY["source"].values():
                await context.send_message(azure_translate(text, from_language, to_language))
                return

        else:
            source_lang = DEEPL_TRANSLATION_KEY["source"][from_language.lower()]

        await context.send_message(deepl_translator.translate_text(
            text,
            source_lang=source_lang,
            target_lang=DEEPL_TRANSLATION_KEY["target"][to_language.lower()]
        ))
