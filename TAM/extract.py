import collections
import tqdm

import TAM.utils as utils

def extract_advN(filename, source, file_id, accepted_nouns):

	freqs = collections.defaultdict(int)

	prefs_freqs = collections.defaultdict(int)
	nouns_freqs = collections.defaultdict(int)

	for sentence in tqdm.tqdm(utils.read(filename, source)):
		for token in sentence.sentence:
			if token.pos == "NOUN" and "-" in token.form:
				formsplit = token.form.rsplit("-", 1)
				if formsplit[1] in accepted_nouns:
					freqs[token.form] += 1
					prefs_freqs[formsplit[0]] += 1
					nouns_freqs[formsplit[1]] += 1

	with open(f"../data/output/{source}_{file_id}.compunds.tsv", "w", encoding="utf-8") as fout:
		for key, f in freqs.items():
			print(f"{f}\t{key}", file=fout)

	with open(f"../data/output/{source}_{file_id}.prefs.tsv", "w", encoding="utf-8") as fout:
		for key, f in prefs_freqs.items():
			print(f"{f}\t{key}", file=fout)
	
	with open(f"../data/output/{source}_{file_id}.nouns.tsv", "w", encoding="utf-8") as fout:
		for key, f in nouns_freqs.items():
			print(f"{f}\t{key}", file=fout)


def extract_detADVN(filename, source, file_id, accepted_nouns):
	freqs = collections.defaultdict(int)
	
	adverbs_freqs = collections.defaultdict(int)
	nouns_freqs = collections.defaultdict(int)

	for sentence in tqdm.tqdm(utils.read(filename, source)):
		candidates = []

		for tok_id, token in enumerate(sentence.sentence):
			if token.pos == "ADV" and \
				tok_id > 2 and \
					tok_id < len(sentence.sentence)-2:
					candidates.append(tok_id)


		for c_id in candidates:
			
			adverb_object = sentence.sentence[c_id]
			
			pprevious_object = sentence.sentence[c_id-2]
			previous_object = sentence.sentence[c_id-1]
			
			next_object = sentence.sentence[c_id+1]
			nnext_object = sentence.sentence[c_id+2]
			
			if previous_object.pos == "DET":                                                # DET ADV ? ? case

				determiner_object = previous_object
				
				if (
					next_object.pos == "NOUN" and \
					((determiner_object.deprel == "" or determiner_object.head == adverb_object.id) or \
					(adverb_object.deprel == "" or adverb_object.head == next_object.id))
				):                                                                          # DET ADV NOUN case
					
					noun_object = next_object
					ngramtype = "DET ADV NOUN"
					

					if noun_object.form in accepted_nouns:
						freqs[(adverb_object.form, noun_object.form)] += 1
						adverbs_freqs[adverb_object.form] += 1
						nouns_freqs[noun_object.form] += 1
						# freqs[(determiner_object.form, adverb_object.form, noun_object.form)] += 1
						


				elif (
					next_object.pos == "ADV" and \
					nnext_object.pos == "NOUN" and \
					((determiner_object.deprel == "" or determiner_object.head == nnext_object.id) or \
					(adverb_object.deprel == "" or adverb_object.head == nnext_object.id) or \
					(next_object.deprel == "" or next_object.head == nnext_object.id))
				):                                                                          # DET ADV ADV NOUN case
					
					noun_object = nnext_object
					adverb_object.form = adverb_object.form + " " + next_object.form
					ngramtype = "DET ADV NOUN"
					

					if noun_object.form in accepted_nouns:
						freqs[(adverb_object.form, noun_object.form)] += 1
						adverbs_freqs[adverb_object.form] += 1
						nouns_freqs[noun_object.form] += 1
						# freqs[(determiner_object.form, adverb_object.form, noun_object.form)] += 1
	  					

				elif (
					next_object.pos == "ADJ" and \
					nnext_object.pos == "NOUN" and \
					((determiner_object.deprel == "" or determiner_object.head == nnext_object.id) or \
					(adverb_object.deprel == "" or adverb_object.head == nnext_object.id))
				):                                                                          # DET ADV ADJ NOUN case
					
					noun_object = nnext_object
					adj_object = next_object
					ngramtype = "DET ADV ADJ NOUN"


					if noun_object.form in accepted_nouns:
						freqs[(adverb_object.form, noun_object.form)] += 1
						adverbs_freqs[adverb_object.form] += 1
						nouns_freqs[noun_object.form] += 1
						# freqs[(determiner_object.form, adverb_object.form, adj_object.form, noun_object.form)] += 1
	  					


			if pprevious_object.pos == "DET":                                               # DET ? ADV ? case

				determiner_object = pprevious_object

				if (
					previous_object.pos == "ADJ" and \
					next_object.pos == "NOUN" and \
					((determiner_object.deprel == "" or determiner_object.head == next_object.id) or \
					(adverb_object.deprel == "" or adverb_object.head == next_object.id))
				):                                                                          # DET ADJ ADV NOUN case

					noun_object = next_object
					adj_object = previous_object
					ngramtype = "DET ADJ ADV NOUN"
					
					
					if noun_object.form in accepted_nouns:
						freqs[(adverb_object.form, noun_object.form)] += 1
						adverbs_freqs[adverb_object.form] += 1
						nouns_freqs[noun_object.form] += 1
						# freqs[(determiner_object.form, adj_object.form, adverb_object.form, noun_object.form)] += 1
	  					


	with open(f"../data/output/{source}_{file_id}.ngrams.tsv", "w", encoding="utf-8") as fout:
		for key, f in sorted(freqs.items(), key=lambda x: -x[1]):
			if f > 0:
				print(f"{f}\t{' '.join(key)}", file=fout)  

	with open(f"../data/output/{source}_{file_id}.advs.tsv", "w", encoding="utf-8") as fout:
		for key, f in sorted(adverbs_freqs.items(), key=lambda x: -x[1]):
			if f > 0:
				print(f"{f}\t{key}", file=fout)

	with open(f"../data/output/{source}_{file_id}.nouns.tsv", "w", encoding="utf-8") as fout:
		for key, f in sorted(nouns_freqs.items(), key=lambda x: -x[1]):
			if f > 0:
				print(f"{f}\t{key}", file=fout)              


def extract_NOUN(filename, source, file_id, output_directory):

	accepted_chars = "abcdefghijklmnopqrstuvwxyzàèéìòù"
	freqs = collections.defaultdict(int)

	for sentence in tqdm.tqdm(utils.read(filename, source)):
		for token in sentence.sentence:
			if token.pos == "NOUN":
				if all(c.lower() in accepted_chars or c in ["-", ".", " "] for c in token.form) and any(c not in ["-", ".", " "] for c in token.form):
					freqs[token.form] += 1

	with open(output_directory.joinpath(f"{source}_{file_id}.NOUNS.tsv"), "w", encoding="utf-8") as fout:
		for key, f in sorted(freqs.items()):
			print(f"{f}\t{key}", file=fout)


if __name__ == "__main__":
	import utils

	accepted_nouns = utils.load_NOUNS("../data/output/REPUBBLICA_01.NOUNS.tsv", 2)

# TODO: extract nouns
# TODO: only consider base nouns more frequent than X