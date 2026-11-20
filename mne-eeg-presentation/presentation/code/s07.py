files = eegbci.load_data(1, [6, 10, 14],
                         update_path=False)
for f in files:
    print(f.name, f.stat().st_size // 1000, "kB")
