
import unicodedata
from nltk.stem import PorterStemmer

class Tokenizer:
    def __init__(self):
        self._stemmer = PorterStemmer()

    def tokenize_content(self, important_content: str) -> list:
        currentToken = ""
        token_list = []
        total_characters = len(important_content)

        for characterIndex in range(total_characters):
            character = important_content[characterIndex]
            if character.isalnum():
                currentToken += character

            else:
                if currentToken != "":
                    normalized_token = self.normalize_token(currentToken)
                    token_list.append(normalized_token)
                currentToken = ""

            if characterIndex == total_characters - 1:
                if currentToken != "":
                    normalized_token = self.normalize_token(currentToken)
                    token_list.append(normalized_token)

        return token_list

    def normalize_token(self, text):
        try:
            text = unicodedata.normalize('NFD', text.lower())
            return self._stemmer.stem(text)
        except Exception:
            return ""