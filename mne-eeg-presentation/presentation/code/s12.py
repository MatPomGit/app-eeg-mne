ann = raw.annotations
desc = [d for d in ann.description
        if d[0] == "T"]
cnt = [desc.count(k) for k in ("T0","T1","T2")]
print("T0/T1/T2:", *cnt)
