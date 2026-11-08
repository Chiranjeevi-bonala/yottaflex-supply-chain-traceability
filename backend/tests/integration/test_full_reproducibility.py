import hashlib
from data.generators.pipeline import run_pipeline
from data.generators.config import FIXED_SEED

def compute_dataset_sha256(data_dict):
    h = hashlib.sha256()
    for table_name in sorted(data_dict.keys()):
        rows = data_dict[table_name]
        h.update(f"table:{table_name}:{len(rows)}:".encode())
        for row in rows:
            for k in sorted(row.keys()):
                h.update(f"{k}={row[k]};".encode())
    return h.hexdigest()

def test_full_reproducibility_sha256():
    """
    Executes two independent pipeline runs with seed 20261022
    and verifies row counts, primary keys, and SHA-256 content hashes match 100%.
    """
    seed = FIXED_SEED
    data_run1, md5_1 = run_pipeline(scale_name="starter", seed=seed, export=False)
    data_run2, md5_2 = run_pipeline(scale_name="starter", seed=seed, export=False)

    sha256_run1 = compute_dataset_sha256(data_run1)
    sha256_run2 = compute_dataset_sha256(data_run2)

    assert md5_1 == md5_2, f"MD5 mismatch: {md5_1} != {md5_2}"
    assert sha256_run1 == sha256_run2, f"SHA-256 mismatch: {sha256_run1} != {sha256_run2}"

    # Verify all primary keys match in order
    for table_name in data_run1:
        assert len(data_run1[table_name]) == len(data_run2[table_name])
