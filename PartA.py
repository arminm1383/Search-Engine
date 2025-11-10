import sys
import unicodedata

class WordFrequencies:
    def tokenize(self, text_file_path):

        # Runtime Complexity: O(n)

        try:
            with open(text_file_path, "r") as token_file:
                file_contents = token_file.read()
        except Exception as e:
            print(f'ERROR: File does not exist: {e}')

        currentToken = ""
        token_list = []
        total_characters = len(file_contents)

        for characterIndex in range(total_characters): # O(n)
            character = file_contents[characterIndex]
            if character.isalnum():
                currentToken += character

            else:
                if currentToken != "":
                    normalized_token = self.normalize_token(currentToken)
                    token_list.append(normalized_token) # O(1)
                currentToken = ""

            if characterIndex == total_characters - 1:
                if currentToken != "":
                    normalized_token = self.normalize_token(currentToken)
                    token_list.append(normalized_token)

        return token_list

    def normalize_token(self, text):
        # Runtime Complexity: O(n)
        try:
            return unicodedata.normalize('NFD', text.lower())
        except Exception:
            return ""

    def computeWordFrequencies(self, token_list):
        # Runtime Complexity: O(n)

        word_frequencies = {}
        for current_token in token_list:
            normalized_token = self.normalize_token(current_token)
            if normalized_token not in word_frequencies.keys():
                word_frequencies[normalized_token] = 1
            else:
                word_frequencies[normalized_token] += 1

        return word_frequencies

    def print_frequencies(self, frequencies):
        # Runtime Complexity: O(n log n)

        sorted_frequencies = dict(sorted(frequencies.items(), key=lambda item: item[1], reverse = True))
        for token, count in sorted_frequencies.items():
            print(f'{token}\t{count}')

if __name__ == "__main__":
    word_frequencies_instance = WordFrequencies()
    tokens = word_frequencies_instance.tokenize(sys.argv[1])
    frequencies = word_frequencies_instance.computeWordFrequencies(tokens)
    word_frequencies_instance.print_frequencies(frequencies)
