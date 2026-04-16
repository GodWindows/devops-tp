from entities.greeting import AudienceLevel


class GreetingTemplateService:
    _TEMPLATES: dict[str, dict[AudienceLevel, str]] = {
        "fr": {
            AudienceLevel.CASUAL: "Salut {name}",
            AudienceLevel.FORMAL: "Bonjour {name}",
            AudienceLevel.VIP: "Bienvenue, tres cher {name}",
        },
        "en": {
            AudienceLevel.CASUAL: "Hi {name}",
            AudienceLevel.FORMAL: "Hello {name}",
            AudienceLevel.VIP: "Welcome, dear {name}",
        },
        "es": {
            AudienceLevel.CASUAL: "Hola {name}",
            AudienceLevel.FORMAL: "Buenos dias {name}",
            AudienceLevel.VIP: "Bienvenido, estimado {name}",
        },
    }

    def build_message(self, *, name: str, language: str, audience: AudienceLevel, excited: bool) -> str:
        language_templates = self._TEMPLATES.get(language)
        if language_templates is None:
            raise ValueError(f"Unsupported language: {language}")

        message = language_templates[audience].format(name=name)
        punctuation = "!" if excited else "."
        return f"{message}{punctuation}"

    def list_supported_languages(self) -> list[str]:
        return sorted(self._TEMPLATES.keys())
