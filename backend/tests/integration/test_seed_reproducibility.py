from data.generators.pipeline import run_pipeline

def test_fixed_seed_deterministic_reproducibility():
    """
    Executes the data pipeline twice with the same fixed seed (20261022)
    and asserts that row counts and computed MD5 checksums are 100% identical.
    """
    seed = 20261022
    data_run1, md5_run1 = run_pipeline(scale_name="starter", seed=seed, export=False)
    data_run2, md5_run2 = run_pipeline(scale_name="starter", seed=seed, export=False)

    # 1. Compare row counts across all 16 tables
    for table_name in data_run1.keys():
        count1 = len(data_run1[table_name])
        count2 = len(data_run2[table_name])
        assert count1 == count2, f"Table {table_name} row count mismatch: {count1} != {count2}"

    # 2. Compare exact checksums
    assert md5_run1 == md5_run2, f"Checksum mismatch: {md5_run1} != {md5_run2}"

