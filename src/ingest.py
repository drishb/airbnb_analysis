def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    stats = {"rows_in": len(df)}

    zero_price = int((df["price"] == 0).sum())
    df = df.loc[df["price"] > 0].copy()
    stats["zero_price_dropped"] = zero_price

    lo = df["price"].quantile(config.WINSORIZE_LOWER_PCT)
    hi = df["price"].quantile(config.WINSORIZE_UPPER_PCT)
    df["price_winsorized"] = df["price"].clip(lower=lo, upper=hi)
    df["log_price"] = np.log(df["price_winsorized"])

    # req 5: no imputation. Asserted rather than assumed, because a later
    # refactor that fills these would silently destroy the inactivity
    # indicator in section 4.9.
    assert df["last_review"].isna().sum() > 0
    assert df["reviews_per_month"].isna().sum() > 0

    return df, stats