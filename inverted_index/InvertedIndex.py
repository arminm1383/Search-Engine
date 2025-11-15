import json
import unicodedata
from pathlib import Path
from bs4 import BeautifulSoup
from tokenizer.Tokenizer import Tokenizer

class InvertedIndex:
    def __init__(self, corpus, disk):
        self._corpus = Path(corpus) # UCI dataset
        self._inverted_index_map = {}
        self._batch_index = {}
        self._important_tags = ["h1", "h2", "h3", "strong", "title"]
        self._all_tags = ["p", "div", "span", "li", "a", "h1", "h2", "h3", "strong", "title"]
        self._tokenizer = Tokenizer()
        self._disk = Path(disk) # Local Disk
        self._output_path = self._disk / "inverted_index.json"
        self._batch_capacity = 1000
        self._batch_size = 0
        self._batch_ID = 0

    def build_index(self):
        # Builds the index by parsing JSON, tokenizing text, and returning tokens for the map itself
        filtered_corpus = self._corpus.rglob('*.json')
        for domain in filtered_corpus:
            important_content = []
            remaining_content = []
            # Iterate and Read JSON
            with open(domain, "r", encoding="utf-8") as json_file:
                json_object = json.load(json_file)

            # Parse JSON and Extract HTML
            html_contents = json_object["content"]
            parsed_html = BeautifulSoup(html_contents, "lxml")

            # Identify HTML Tags and Extract Content
            html_tags = parsed_html.find_all()
            for item in html_tags:
                text = item.get_text(separator=" ", strip=True)

                if item.name in self._important_tags:
                    important_content.append(text)
                else:
                    remaining_content.append(text)

            # Tokenize Content
            important_tokens = self._tokenizer.tokenize_content(" ".join(important_content))
            remaining_tokens = self._tokenizer.tokenize_content(" ".join(remaining_content))
            combined_tokens = important_tokens + remaining_tokens

            # Identify Token Frequencies and Add Posting
            word_frequencies = self.compute_word_frequencies(combined_tokens)
            try:
                doc_ID = json_object["url"]
            except KeyError:
                doc_ID = str(domain)

            # Add Posting to Batch Index and Check for Capacity
            self.add_posting(doc_ID, word_frequencies)
            self._batch_size+=1
            self.check_batch_capacity()
        if self._batch_size > 0:
            self.write_batch_to_disk()
            self._batch_index = {}
            self._batch_size = 0

    def add_posting(self, doc_ID, word_frequencies):
        for token, freq in word_frequencies.items():
            if token not in self._batch_index:
                self._batch_index[token] = {}
            self._batch_index[token][doc_ID] = freq

    def check_batch_capacity(self):
        # Checks for Batch Capacity. Writes to disk if full.
        if self._batch_size >= self._batch_capacity:
            self.write_batch_to_disk()
            # Reset Global Batch Properties
            self._batch_index = {}
            self._batch_size = 0

    def compute_word_frequencies(self, token_list):
        # Helper function to count frequencies
        word_frequencies = {}
        for current_token in token_list:
            try:
                normalized_token = unicodedata.normalize('NFD', current_token.lower())
            except Exception:
                normalized_token = ""

            if normalized_token not in word_frequencies.keys():
                word_frequencies[normalized_token] = 1
            else:
                word_frequencies[normalized_token] += 1

        return word_frequencies

    def write_batch_to_disk(self):
        # Write to Disk
        disk_path = self._disk / f"partial_index_{self._batch_ID}.json"
        with open(disk_path, "w", encoding="utf-8") as disk:
            json.dump(self._batch_index, disk)
        self._batch_ID += 1

    def get_file_size(self):
        # Return Size (KB)
        return self._output_path.stat().st_size / 1024

    def build_final_index(self):
        for partial_file in self._disk.glob("partial_index_*.json"):
            with open(partial_file, "r", encoding = "utf-8") as f:
                batch = json.load(f)

            for token, postings in batch.items():
                if token not in self._inverted_index_map:
                    self._inverted_index_map[token] = {}

                for doc_id, freq in postings.items():
                    self._inverted_index_map[token][doc_id] = freq

        return self._inverted_index_map

    def get_document_count(self):
        document_set = set()
        for postings in self._inverted_index_map.values():
            for document in postings:
                document_set.add(document)
        return len(document_set)

    def get_unique_tokens(self):
        return len(self._inverted_index_map)

    def write_final_index_to_disk(self):
        with open(self._output_path, "w", encoding = "utf-8") as disk:
            json.dump(self._inverted_index_map, disk)

    def write_result_stats(self, time):
        with open(self._disk / "index_stats.txt", "w", encoding = "utf-8") as file_object:
            file_object.write(f'DOCUMENT COUNT: {str(self.get_document_count())}\n')
            file_object.write(f'TOKEN COUNT: {str(self.get_unique_tokens())}\n')
            file_object.write(f'FILE SIZE: {str(self.get_file_size())}\n')
            file_object.write(f'TOTAL TIME: {str(time)}\n')