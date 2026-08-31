# Topic Model

## Baseline vocabulary

- Vocabulary: 1482 terms (unigrams + bigrams, min_df=20)
- Selected k = **8** by UMass coherence (-3.1441), margin over runner-up 0.0155

| k | coherence | reconstruction error |
|---:|---:|---:|
| 5 | -3.2500 | 173.61 |
| 6 | -3.1596 | 172.75 |
| 7 | -3.2539 | 171.94 |
| 8 | -3.1441 | 171.15 |

| Topic | Top terms |
|---:|---|
| 0 | room, private, private room, bath, room private, cozy, bathroom, bed, room bath, cozy private |
| 1 | hollywood, hills, hollywood hills, beverly, beverly hills, studio, west, west hollywood, heart, apartment |
| 2 | beach, venice, venice beach, studio, long beach, long, bungalow, walk, steps, near |
| 3 | house, guest, guest house, private guest, beach house, pool, la, private, beautiful, charming |
| 4 | bedroom, private, private bedroom, bath, bathroom, master, apartment, master bedroom, bedroom bath, cozy |
| 5 | home, away, away home, home away, beautiful, la, cozy, family, modern, pool |
| 6 | los, angeles, los angeles, downtown, studio, apartment, feliz, downtown los, los feliz, la |
| 7 | santa, monica, santa monica, apartment, monica beach, ocean, heart santa, location, ucla, view |

**Why this run is not used.** Most topics here reproduce place names and room types — information already held in `neighbourhood`, `room_type`, and the five distance columns from task 2.0. Using these loadings as clustering features would weight geography a second time. The suppressed run above is used instead; this one is the evidence for that choice.

## Suppressed vocabulary (used)

- Vocabulary: 855 terms (unigrams + bigrams, min_df=20)
- Selected k = **5** by UMass coherence (-3.9543), margin over runner-up 0.1363

| k | coherence | reconstruction error |
|---:|---:|---:|
| 5 | -3.9543 | 164.45 |
| 6 | -4.1194 | 163.39 |
| 7 | -4.1047 | 162.35 |
| 8 | -4.0906 | 161.33 |

| Topic | Top terms |
|---:|---|
| 0 | cozy, cozy near, clean, quiet, cozy heart, parking, close, entrance, cozy quiet, location |
| 1 | modern, luxury, parking, new, pool, views, spacious, close, location, ocean |
| 2 | beautiful, master, close, spacious, large, pool, quiet, beautiful cozy, location, parking |
| 3 | near, spacious, lax, charming, near lax, quiet, cozy near, studios, pool, large |
| 4 | heart, charming, luxury, cozy heart, spacious, sunny, modern heart, large, amazing, place |

### Hypothesis check (req 34)

The tourism / upmarket / commercial grouping was a prior, not an input. Overlap with the derived topics:

|   topic |   tourism_hits | tourism_terms   |   upmarket_hits | upmarket_terms   |   commercial_hits | commercial_terms   |
|--------:|---------------:|:----------------|----------------:|:-----------------|------------------:|:-------------------|
|       0 |              0 | —               |               0 | —                |                 0 | —                  |
|       1 |              0 | —               |               2 | luxury, modern   |                 0 | —                  |
|       2 |              0 | —               |               0 | —                |                 0 | —                  |
|       3 |              0 | —               |               0 | —                |                 0 | —                  |
|       4 |              0 | —               |               1 | luxury           |                 0 | —                  |

Sensitivity to `min_df` (topic-set Jaccard vs. the min_df=20 fit):

|   min_df |   vocabulary |   mean_topic_overlap |   min_topic_overlap |
|---------:|-------------:|---------------------:|--------------------:|
|       10 |         1649 |             0.679654 |            0.428571 |
|       20 |          855 |             1        |            1        |
|       50 |          360 |             0.727273 |            0.666667 |
