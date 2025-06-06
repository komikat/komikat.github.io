---
layout: post
title: "Establishing Communication"
comments: false
---

![The Creation of Adam – Michelangelo](https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg/1920px-Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg)  
*Michelangelo, The Creation of Adam (c. 1512)*

> Section 3.3 - Reversing the Source Sentences

> While the LSTM is capable of solving problems with long term dependencies, we discovered that the LSTM learns much better when the source sentences are reversed (the target sentences are not reversed). By doing so, the LSTM’s test perplexity dropped from 5.8 to 4.7, and the test BLEU scores of its decoded translations increased from 25.9 to 30.6.

> While we do not have a complete explanation to this phenomenon, we believe that it is caused by the introduction of many short-term dependencies to the dataset. Normally, when we concatenate a source sentence with a target sentence, each word in the source sentence is far from its corresponding word in the target sentence. As a result, the problem has a large “minimal time lag”. By reversing the words in the source sentence, the average distance between corresponding words in the source and target language is unchanged. However, the first few words in the source language are now very close to the first few words in the target language, so the problem’s minimal time lag is greatly reduced. Thus, backpropagation has an easier time “establishing communication” between the source sentence and the target sentence, which in turn results in substantially improved overall performance.

> — *Ilya Sutskever, Oriol Vinyals & Quoc V. Le*, “Sequence to Sequence Learning with Neural Networks,” *Advances in Neural Information Processing Systems 27* (2014). [arXiv:1409.3215](https://arxiv.org/abs/1409.3215)
