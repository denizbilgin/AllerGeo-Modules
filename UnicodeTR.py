from typing import AnyStr


class UnicodeTR(str):
    CHARMAP = {
        "to_upper": {
            u"ı": u"I",
            u"i": u"İ",
        },
        "to_lower": {
            u"I": u"ı",
            u"İ": u"i",
        }
    }

    def lower(self) -> AnyStr:
        for key, value in self.CHARMAP.get("to_lower").items():
            self = self.replace(key, value)
        return self.lower()

    def upper(self) -> AnyStr:
        for key, value in self.CHARMAP.get("to_upper").items():
            self = self.replace(key, value)
        return self.upper()

    def capitalize(self) -> AnyStr:
        return UnicodeTR(self[0]).upper() + UnicodeTR(self[1:]).lower()
