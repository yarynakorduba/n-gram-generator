### How data was generated?

1. We took a real articles dataset
2. Rejected all the articles, which have less than 20 sentences.
3. Based on these articles, we generated our articles using ngram model with `n=5`.
4. The number of sentences of each article is the number of the sentences in the original article + 10
5. This number is bound by a minimum of 50 sentences and maximum of 100 sentences.
