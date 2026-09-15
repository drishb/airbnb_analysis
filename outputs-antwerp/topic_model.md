# Topic Model

## Baseline vocabulary

- Vocabulary: 112 terms (unigrams + bigrams, min_df=20)
- Selected k = **5** by UMass coherence (-2.7499), margin over runner-up 0.0614

| k | coherence | reconstruction error |
|---:|---:|---:|
| 5 | -2.7499 | 42.55 |
| 6 | -2.8113 | 41.82 |
| 7 | -2.8169 | 41.23 |
| 8 | -2.8152 | 40.61 |

| Topic | Top terms |
|---:|---|
| 0 | apartment, spacious, apartment antwerp, bright, beautiful, central, view, location, trendy, terrace |
| 1 | appartement, antwerpen, centrum, studio, hartje, zuid, modern, loft, kamer, duplex |
| 2 | room, house, private, cosy, near, cosy room, station, private room, spacious, close |
| 3 | antwerp, heart, heart antwerp, flat, place, apartment heart, lodge, loft, apt, house |
| 4 | city, center, studio, city center, antwerp city, center antwerp, city centre, centre, cosy, antwerp |

**Why this run is not used.** Most topics here reproduce place names and room types — information already held in `neighbourhood`, `room_type`, and the five distance columns from task 2.0. Using these loadings as clustering features would weight geography a second time. The suppressed run above is used instead; this one is the evidence for that choice.

## Suppressed vocabulary (used)

- Vocabulary: 69 terms (unigrams + bigrams, min_df=20)
- Selected k = **5** by UMass coherence (-3.0110), margin over runner-up 0.0236

| k | coherence | reconstruction error |
|---:|---:|---:|
| 5 | -3.0110 | 37.80 |
| 6 | -3.0346 | 37.01 |
| 7 | -3.1097 | 36.38 |
| 8 | -3.1161 | 35.78 |

| Topic | Top terms |
|---:|---|
| 0 | center, city, city center, close, near city, cozy, near, new, flats, beautiful |
| 1 | cosy, near, trendy, flat, south, appartment, historic, garden, floor, parking |
| 2 | heart, flat, place, lodge, luxury, cozy, modern, location, view, charming |
| 3 | spacious, central, terrace, bright, view, near, charming, cozy, modern, trendy |
| 4 | centre, city centre, city, historic, beautiful, modern, historical, nice, close, near |

### Hypothesis check (req 34)

The tourism / upmarket / commercial grouping was a prior, not an input. Overlap with the derived topics:

|   topic |   tourism_hits | tourism_terms   |   upmarket_hits | upmarket_terms   |   commercial_hits | commercial_terms   |
|--------:|---------------:|:----------------|----------------:|:-----------------|------------------:|:-------------------|
|       0 |              0 | —               |               0 | —                |                 0 | —                  |
|       1 |              0 | —               |               1 | historic         |                 0 | —                  |
|       2 |              0 | —               |               2 | luxury, modern   |                 0 | —                  |
|       3 |              0 | —               |               1 | modern           |                 0 | —                  |
|       4 |              0 | —               |               2 | historic, modern |                 0 | —                  |

Sensitivity to `min_df` (topic-set Jaccard vs. the min_df=20 fit):

|   min_df |   vocabulary |   mean_topic_overlap |   min_topic_overlap |
|---------:|-------------:|---------------------:|--------------------:|
|       10 |          155 |             0.671329 |            0.538462 |
|       20 |           69 |             1        |            1        |
|       50 |           33 |             0.757576 |            0.666667 |
