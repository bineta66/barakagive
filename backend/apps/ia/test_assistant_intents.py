from django.test import SimpleTestCase

from apps.ia.assistant_intents import classify_assistant_intent


class ExecutiveAssistantIntentTests(SimpleTestCase):
    def test_confirmation_variants_are_accepted(self):
        for text in (
            "confirmer", "Comfirmer", "oui je comfirme", "je confirme le projet",
            "c'est confirmé",
        ):
            with self.subTest(text=text):
                self.assertEqual(
                    classify_assistant_intent(text, "AWAITING_CONFIRMATION"),
                    "PROJECT_CREATION_CONFIRM",
                )

    def test_negative_or_ambiguous_confirmation_is_not_accepted(self):
        for text in (
            "oui", "Je ne confirme pas", "Je veux corriger le budget avant de confirmer",
            "Que signifie confirmer ?", "« confirmer » pour enregistrer ce projet",
        ):
            with self.subTest(text=text):
                self.assertNotEqual(
                    classify_assistant_intent(text, "AWAITING_CONFIRMATION"),
                    "PROJECT_CREATION_CONFIRM",
                )

    def test_current_message_routes_scope_without_history(self):
        self.assertEqual(classify_assistant_intent("C'est quoi un token ?"), "OUT_OF_SCOPE")
        self.assertEqual(classify_assistant_intent("Fais-moi le bilan de mon ONG"), "ONG_SUMMARY")
        self.assertEqual(classify_assistant_intent("Liste mes projets"), "PROJECT_LIST")
        self.assertEqual(
            classify_assistant_intent("Quel est mon budget ?", "description"),
            "ONG_BUSINESS_QUESTION",
        )

