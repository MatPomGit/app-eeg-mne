for ch in ["C3", "Cz", "C4"]:
    h, f = [100 * erd[c].get_data(
            picks=[ch], **win).mean()
            for c in ("hands", "feet")]
    print(ch, round(h), round(f))
