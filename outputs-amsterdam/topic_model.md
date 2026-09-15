# Topic Model

## Baseline vocabulary

- Vocabulary: 808 terms (unigrams + bigrams, min_df=20)
- Selected k = **5** by UMass coherence (-3.2285), margin over runner-up 0.0582

| k | coherence | reconstruction error |
|---:|---:|---:|
| 5 | -3.2285 | 130.31 |
| 6 | -3.3196 | 129.48 |
| 7 | -3.2867 | 128.76 |
| 8 | -3.4100 | 128.03 |

| Topic | Top terms |
|---:|---|
| 0 | apartment, spacious, spacious apartment, pijp, bright, cosy, vondelpark, apartment amsterdam, modern, light |
| 1 | amsterdam, apartment amsterdam, west, amsterdam west, studio, centre amsterdam, heart amsterdam, east, amsterdam east, appartement |
| 2 | city, centre, city centre, center, city center, near, apartment city, near city, close, close city |
| 3 | house, family, garden, family house, home, canal, family home, house garden, spacious, parking |
| 4 | room, private, private room, room amsterdam, cozy, cozy room, studio, bathroom, view, nice |

**Why this run is not used.** Most topics here reproduce place names and room types — information already held in `neighbourhood`, `room_type`, and the five distance columns from task 2.0. Using these loadings as clustering features would weight geography a second time. The suppressed run above is used instead; this one is the evidence for that choice.

## Suppressed vocabulary (used)

- Vocabulary: 538 terms (unigrams + bigrams, min_df=20)
- Selected k = **5** by UMass coherence (-3.3902), margin over runner-up 0.1134

| k | coherence | reconstruction error |
|---:|---:|---:|
| 5 | -3.3902 | 126.04 |
| 6 | -3.5753 | 124.86 |
| 7 | -3.5036 | 123.73 |
| 8 | -3.5672 | 122.65 |

| Topic | Top terms |
|---:|---|
| 0 | city, centre, city centre, center, city center, near, near city, close, close city, lovely |
| 1 | spacious, garden, family, bright, lovely, modern, light, terrace, sunny, spacious family |
| 2 | cozy, beautiful, heart, cozy near, central, balcony, area, bright, near, cozy appartment |
| 3 | cosy, central, near, appartment, cosy near, area, cosy appartment, cosy garden, light, quiet |
| 4 | canal, view, canal view, beautiful, central, great, location, luxurious, amazing, luxury |

### Hypothesis check (req 34)

The tourism / upmarket / commercial grouping was a prior, not an input. Overlap with the derived topics:

|   topic |   tourism_hits | tourism_terms   |   upmarket_hits | upmarket_terms   |   commercial_hits | commercial_terms   |
|--------:|---------------:|:----------------|----------------:|:-----------------|------------------:|:-------------------|
|       0 |              0 | —               |               0 | —                |                 0 | —                  |
|       1 |              0 | —               |               1 | modern           |                 0 | —                  |
|       2 |              1 | central         |               0 | —                |                 0 | —                  |
|       3 |              1 | central         |               0 | —                |                 0 | —                  |
|       4 |              2 | canal, central  |               1 | luxury           |                 0 | —                  |

Sensitivity to `min_df` (topic-set Jaccard vs. the min_df=20 fit):

|   min_df |   vocabulary |   mean_topic_overlap |   min_topic_overlap |
|---------:|-------------:|---------------------:|--------------------:|
|       10 |         1074 |             0.866667 |            0.666667 |
|       20 |          538 |             1        |            1        |
|       50 |          192 |             0.690376 |            0.428571 |
