# Topic Model

## Baseline vocabulary

- Vocabulary: 1371 terms (unigrams + bigrams, min_df=20)
- Selected k = **6** by UMass coherence (-3.4009), margin over runner-up 0.1749

| k | coherence | reconstruction error |
|---:|---:|---:|
| 5 | -3.5759 | 180.88 |
| 6 | -3.4009 | 179.83 |
| 7 | -3.6665 | 178.93 |
| 8 | -3.6788 | 178.01 |

| Topic | Top terms |
|---:|---|
| 0 | copacabana, praia, praia copacabana, copacabana beach, apartamento copacabana, studio, posto, beach, quadra, quadra praia |
| 1 | barra, tijuca, barra tijuca, praia, praia barra, suite, apartamento barra, flat, mar, frente |
| 2 | rio, janeiro, rio janeiro, room, room rio, centro, rock, rock rio, 2016, rio centro |
| 3 | apartamento, apartamento copacabana, quartos, olimpiadas, aconchegante, apartamento quartos, praia, lindo, apartamento aconchegante, proximo |
| 4 | quarto, casa, sala, casal, aconchegante, quarto sala, quarto casal, praia, confortavel, botafogo |
| 5 | ipanema, apartment, beach, bedroom, ipanema beach, near, room, leblon, cozy, apartment ipanema |

**Why this run is not used.** Most topics here reproduce place names and room types — information already held in `neighbourhood`, `room_type`, and the five distance columns from task 2.0. Using these loadings as clustering features would weight geography a second time. The suppressed run above is used instead; this one is the evidence for that choice.

## Suppressed vocabulary (used)

- Vocabulary: 771 terms (unigrams + bigrams, min_df=20)
- Selected k = **5** by UMass coherence (-3.8637), margin over runner-up 0.0109

| k | coherence | reconstruction error |
|---:|---:|---:|
| 5 | -3.8637 | 169.74 |
| 6 | -3.8746 | 168.75 |
| 7 | -4.0038 | 167.76 |
| 8 | -3.9632 | 166.82 |

| Topic | Top terms |
|---:|---|
| 0 | beach, near, near beach, cozy, block, close, close beach, view, block beach, penthouse |
| 1 | aconchegante, coracao, conjugado, charmoso, aconchegante coracao, cantinho, sala, confortavel, melhor, espaco |
| 2 | olimpiadas, 2016, olimpiadas 2016, alugo, aluguel, alugo olimpiadas, aluguel olimpiadas, olympic, games, olympic games |
| 3 | quadra, frente, posto, carnaval, excelente, lindo, copa, coracao, sala, localizacao |
| 4 | proximo, metro, proximo metro, olimpico, maracana, perto, proximo olimpico, proximo maracana, lado, perto metro |

### Hypothesis check (req 34)

The tourism / upmarket / commercial grouping was a prior, not an input. Overlap with the derived topics:

|   topic |   tourism_hits | tourism_terms   |   upmarket_hits | upmarket_terms   |   commercial_hits | commercial_terms   |
|--------:|---------------:|:----------------|----------------:|:-----------------|------------------:|:-------------------|
|       0 |              1 | beach           |               0 | —                |                 0 | —                  |
|       1 |              0 | —               |               0 | —                |                 0 | —                  |
|       2 |              0 | —               |               0 | —                |                 0 | —                  |
|       3 |              0 | —               |               0 | —                |                 0 | —                  |
|       4 |              0 | —               |               0 | —                |                 0 | —                  |

Sensitivity to `min_df` (topic-set Jaccard vs. the min_df=20 fit):

|   min_df |   vocabulary |   mean_topic_overlap |   min_topic_overlap |
|---------:|-------------:|---------------------:|--------------------:|
|       10 |         1448 |             0.592337 |            0.176471 |
|       20 |          771 |             1        |            1        |
|       50 |          341 |             0.804662 |            0.538462 |
