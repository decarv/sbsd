# sbsd - Sistema de Busca Semântico de Documentos

**_Under active development._**

## Pesquisa

### Relatório do Primeiro Semestre

A pesquisa inicial propunha a investigação de _embeddings_ e busca vetorial e sua utilização na criação de sistemas de busca semânticos. Como resultado da pesquisa, eu pretendo criar um sistema de busca semântico para o sistema de busca de teses da USP, disponível em https://teses.usp.br/. O sistema de busca deve envolver texto e imagem. Quando se lê, abaixo, sobre texto, o mesmo vale para imagem.

#### Por que um sistema de busca semântico?
Minha suposição inicial é de que um sistema de busca semântico é melhor para buscar textos do que sistemas tradicionais de busca, principalmente quando envolve recuperação de conhecimento. Quando recuperar conhecimento envolve a combinação de palavras e a busca dessas palavras em textos, um sistema deve considerar o sentido semântico de cada palavra individual, o contexto da busca, o sentido semântico de todas as palavras juntas. Em um sistema comum de recuperação de conhecimento, existem heurísticas de busca por frequência de palavras em um texto para recuperá-lo, o que não é suficiente para conseguir um resultado de busca relevante.

#### O que são _embeddings_ e por que utilizá-los? 
São formas de representar texto com números, através da codificação desse texto. Diferentemente de outros métodos de codificação de texto, embeddings conseguem representar relacionamentos entre palavras e sua codificação ajuda em sua utilização em algoritmos de aprendizagem de máquina. Com embeddings, a similaridade semântica entre dois textos pode ser computada de forma trivial por meio do produto interno de suas representações.

Embeddings são gerados a partir de um modelo de aprendizagem de máquina. Esses modelos são treinados com bilhões ou mais de um trilhão de palavras obtidas da internet. Eles resultam em algo semelhante a uma tabela, capazes de receber texto como input e retornar uma representação vetorial desse texto. Esses modelos são treinados para serem capazes de generalizar para uma ampla gama de textos, de várias áreas, mas é possível ajustar tais modelos para gerar melhores representações para os dados com que se está trabalhando. Ajuste fino de um modelo (fine-tuning) é o processo de ajustar um modelo para trabalhar com dados de um domínio específico. A forma de avaliar um modelo que gera embeddings de texto é por MSMARCO Passage Ranking ou STS (Semantic Textual Similarity) Benchmark. A forma de avaliar um modelo ajustado tem a mesma ideia: precisa-se de uma tarefa para resolver e que essa tarefa seja avaliada com base em um resultado conhecido.

Referências: 

- https://www.tensorflow.org/text/guide/word_embeddings 
- https://sbert.net/
- https://huggingface.co/tasks/sentence-similarity
- https://dev.to/meetkern/how-to-fine-tune-your-embeddings-for-better-similarity-search-445e

#### O que é uma busca vetorial?

A busca de texto por meio de embeddings envolve a geração de embeddings de todo o domínio de busca, a geração de embedding do texto que se deseja buscar e a busca vetorial deste último no domínio de busca. A busca vetorial é um método usado para encontrar vetores em um espaço multidimensional. Para isso, é feita uma busca de similaridade entre a representação vetorial do texto buscado e os demais vetores no espaço de busca. Esse método de busca é conhecido como Nearest Neighbors. A ideia da busca é encontrar o vetor mais próximo do vetor de busca. Isso, entretanto, pode ser custoso quando o espaço de busca é muito grande. Alguns algoritmos e estruturas de dados podem ser utilizados para realizar busca de similaridade em grande conjuntos de vetores, como o Approximate Nearest Neighbors (ANN). Bases de dados vetoriais são conhecidas por implementar algoritmos e estruturas para busca eficiente de vetores.

Referências:

- http://simsearch.yury.name/
- https://github.com/currentslab/awesome-vector-search

#### Como avaliar um sistema de busca?

Uma forma eficiente de avaliar é classificar os melhores resultados para buscas específicas e medir a qualidade dos resultados baseados em scores para o ranqueamento. Uma boa forma de testar isso é com Discounted Cumulative Gain. DCG mede um ganho baseado na posição da recuperação do documento relevante de uma busca.

Referências:
- https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)
- https://en.wikipedia.org/wiki/Discounted_cumulative_gain

### Relatório dos Experimentos

Ao longo do semestre eu realizei alguns experimentos com embeddings e com buscas vetoriais, usando dados coletados do site de teses da USP. A forma de coleta de dados foi por um raspador, o código fonte pode ser encontrado em "src" no repositório do sbsd. Os experimentos podem ser encontrados no diretório "experiments" no repositório do sbsd.

#### Experimento 1

No primeiro experimento que realizei, tentei usar toda a informação de alguns .pdfs selecionados das teses para criar embeddings. Além de ter sido demorado para criar cada um embedding, a criação de um embedding por documento se mostrou insatisfatória para a busca, dada que muita informação era perdida, além de que o documento tinha muita sujeira, o que exige trabalho extra de limpeza manual. Essa abordagem resultou em um sistema lento para ser criado e trabalhoso. Ou seja, não resultou em um bom sistema para fazer a busca.


#### Experimento 2

No segundo experimento que realizei, usei apenas as informações de metadados contidas no site de teses, sem utilizar a tese em si. Os metadados são título, resumo e palavras-chave. Juntei esses 3 em um texto só para gerar cada embedding. O tempo de criação de tudo é em torno de alguns minutos. Com isso, fui capaz de criar um sistema de busca que abarcava todas as teses do site de tese da USP. O sistema foi capaz de obter resultados em menos de 1 segundo. Entretanto, notou-se que a busca foi insatisfatória em algumas instâncias. 

Para demonstrar isso, estabeleci o texto de busca "ddos attack". A busca encontrou o vetor mais similar em 0.19s e o resultado retornado foi:

    1. Title:  Mitigating DDoS attacks on IoT through machine learning and network functions virtualization
    Author:  Oliveira, Guilherme Werneck de

Minha suposição é de que, se esse valor retornado é o mais relevante para "ddos attack", ele deve também ser o mais relevante, ou pelo menos perder para algum mais relevante ainda, para "ddos attack and machine learning". Mas não foi isso que aconteceu, ao buscar por "ddos attack and machine learning", a busca encontrou:

    1. Title:  Machine learning in complex networks
    Author:  Breve, Fabricio Aparecido
    2. Title:  Architecture and development of a real-time multiple content generator system for video games
    Author:  Pereira, Leonardo Tortoro
    3. Title:  Performance prediction of application executed on GPUs using a simple analytical model and machine learning techniques
    Author:  González, Marcos Tulio Amarís
    4. Title:  Mitigating DDoS attacks on IoT through machine learning and network functions virtualization
    Author:  Oliveira, Guilherme Werneck de

Mesmo que sem utilizar métodos formais de avaliação, nota-se que o sistema de busca não foi relevante ao buscar por "ddos attack and machine learning". Minha suposição é de que muita informação era perdida ao criar um único embedding para todos os metadados.

#### Experimento 3

No terceiro experimento que realizei, utilizei os mesmos metadados, mas decidi criar os embeddings a partir de cada sentença, e não usando todos os metadados ao mesmo tempo. Essa abordagem resultou em buscas em torno de 50 vezes mais lentas, mas bem mais relevantes.

Considere novamente o texto "ddos attack". A busca demorou 4s e o resultado foi:

    1. Title:  Method for mitigating against distributed denial of service attacks using multi-agent system.
    Author:  Pereira, João Paulo Aragão (Catálogo USP)
    2. Title:  A collaborative architecture against DDOS attacks for cloud computing systems.
    Author:  Almeida, Thiago Rodrigues Meira de (Catálogo USP)
    3. Title:  Mitigating DDoS attacks on IoT through machine learning and network functions virtualization
    Author:  Oliveira, Guilherme Werneck de (Catálogo USP)

Comparado ao resultado anterior, eu consideraria que esses resultados foram tão relevantes quanto para essa busca genérica específica. Para saber mais, eu precisaria comparar os 15 primeiros resultados, por exemplo.

Como segundo teste, busquei o texto "ddos attack and machine learning" e o resultado foi:

    1. Title:  Mitigating DDoS attacks on IoT through machine learning and network functions virtualization
    Author:  Oliveira, Guilherme Werneck de (Catálogo USP)
    2. Title:  Reconfigurable learning system for classification of data using parallel processing
    Author:  Moreira, Eduardo Marmo (Catálogo USP)
    3. Title:  A collaborative architecture against DDOS attacks for cloud computing systems.
    Author:  Almeida, Thiago Rodrigues Meira de (Catálogo USP)

Ou seja, pode-se considerar que houve uma melhora considerável de relevância para essa busca específica.

#### Conclusão Preliminar dos Experimentos

Preliminarmente, notou-se um trade-off entre a qualidade da busca e o tempo levado para buscar e criar o sistema. O sistema que tomou mais para buscar e para criar o sistema resultou em uma qualidade de busca maior. A ideia é que esse sistema seja melhorado em duas frentes, embeddings e busca vetorial. Espera-se que os embeddings resultem em uma maior relevância do resultado de busca e que a busca vetorial resulte em uma maior eficiência (considerando a velocidade do sistema). Afinal, espera-se que um sistema de busca eficiente na web seja capaz de retornar buscas relevantes de forma rápida.

#### Próximos Passos

O primeiro passos a partir de agora é estabelecer uma forma de avaliação da busca, para entender como o sistema pode melhorar. Como referência: https://opensearch.org/blog/semantic-science-benchmarks/

Passos seguintes envolvem melhorar a busca de uma das seguintes formas:
- Ajustando o modelo para os dados que eu possuo;
- Usar mais dados, considerando os documentos .pdf para que a busca possa abranger mais informações de dentro do texto;
- Usar bases de dados vetoriais para a busca.


### Outras referências encontradas

- https://www.deepset.ai/blog/the-beginners-guide-to-text-embeddings
- https://www.elastic.co/blog/how-to-deploy-nlp-text-embeddings-and-vector-search
- https://platform.openai.com/docs/guides/embeddings
- https://rom1504.medium.com/semantic-search-with-embeddings-index-anything-8fb18556443c
- https://towardsdatascience.com/beyond-ctrl-f-44f4bec892e9
- https://github.com/openai/openai-cookbook/blob/main/examples/Semantic_text_search_using_embeddings.ipynb
- https://dev.to/mage_ai/how-to-build-a-search-engine-with-word-embeddings-56jd
- https://huggingface.co/course/chapter5/6?fw=tf
- https://catalog.workshops.aws/semantic-search/en-US/module-1-understand-internal/semantic-search-technology
- Extending Full Text Search for Legal Document Collections Using Word Embeddings
- https://www.scribd.com/document/492791276/Using-Word-Embeddings-for-Text-Search1
- https://blog.dataiku.com/semantic-search-an-overlooked-nlp-superpower
- https://simonwillison.net/2023/Jan/13/semantic-search-answers/
- https://www.buildt.ai/blog/3llmtricks
- https://www.algolia.com/blog/ai/what-is-vector-search/https://qdrant.tech/benchmarks/?gclid=CjwKCAjw__ihBhADEiwAXEazJtsrttmfhWQWIx-xZ2cATXTa2Omoc8RczL_6Bk1NnX_BmNND33xWoxoCqjAQAvD_BwE
- https://cloud.google.com/vertex-ai/docs/matching-engine/overview
- https://developer.huawei.com/consumer/en/doc/development/hiai-Guides/text-embedding-0000001055002819
- https://applyingml.com/resources/search-query-matching/
- https://betterprogramming.pub/openais-embedding-model-with-vector-database-b69014f04433
- Modern Information Retrieval: The Concepts and Technology behind Search
- Word embedding based generalized language model for information retrieval
- Embedding-based Query Language Models
- Lbl2Vec: an embedding-based approach for unsupervised document retrieval on predefined topics
- Neural embedding-based indices for semantic search
- Embedding-based news recommendation for millions of users
- Divide and Conquer: Towards Better Embedding-based Retrieval for Recommender Systems From a Multi-task Perspective
- Embedding based on function approximation for large scale image search
- Pre-training Tasks for Embedding-based Large-scale Retrieval
- QuadrupletBERT: An Efficient Model For Embedding-Based Large-Scale  Retrieval
- A text-embedding-based approach to measuring patent-to-patent technological similarity

Victor Lempitsky. 2012. The Inverted Multi-Index. In Proceedings of the 2012 IEEE
Conference on Computer Vision and Pattern Recognition (CVPR) (CVPR ’12). IEEE
Computer Society, USA, 3069–3076.

Hang Li and Jun Xu. 2014. Semantic Matching in Search. Now Publishers Inc.,
Hanover, MA, USA.

Bhaskar Mitra and Nick Craswell. 2018. An Introduction to Neural Information
Retrieval. Foundations and Trends® in Information Retrieval 13, 1 (December
2018), 1–126.

Chao-Yuan Wu, R. Manmatha, Alexander J. Smola, and Philipp Krähenbühl. 2017.
Sampling Matters in Deep Embedding Learning. CoRR abs/1706.07567 (2017).
arXiv:1706.07567 http://arxiv.org/abs/1706.07567