"""Independent NumPy least-squares oracle for original Pedicularis sensitivity."""
from __future__ import annotations
import argparse
import json
import statistics
import tempfile
from pathlib import Path
from zipfile import ZipFile
from scripts.audit_pedicularis_2013_fruit_set_ancova import load_fruit_rows
from scripts.retrieve_pedicularis_2013_dryad_bytes import verify_zip
from scripts.adjudicate_pedicularis_2013_raw_workbook import SOURCE_SHA256


def numeric_oracle(rows):
    import numpy as np
    n=len(rows)
    fmean=sum(r[3] for r in rows)/n
    x=np.array([[1.,2*r[0]-3,2*r[1]-3,
                 (2*r[0]-3)*(2*r[1]-3),r[3]-fmean] for r in rows])
    y=np.array([r[4] for r in rows])
    b=np.linalg.lstsq(x,y,rcond=None)[0]
    mse=float(np.sum((y-x@b)**2))/(n-5)
    vcov_diag=np.diag(np.linalg.inv(x.T@x))
    ff=[float(b[i]**2/(mse*vcov_diag[i])) for i in range(1,5)]
    return dict(zip(("year","density","interaction","flowers"),ff)), {
        "2005":float(2*(b[2]-b[3])),
        "2011":float(2*(b[2]+b[3])),
    }


def verify(source_zip, receipt):
    blob=Path(source_zip).read_bytes()
    meta=verify_zip(blob)
    if meta["source_sha256"]!=SOURCE_SHA256:
        raise ValueError("original source SHA256 changed")
    with ZipFile(source_zip) as z:
        data=z.read("raw data.xlsx")
    with tempfile.TemporaryDirectory(prefix="pedicularis-numpy-") as tmp:
        workbook=Path(tmp)/"raw data.xlsx"
        workbook.write_bytes(data)
        rows,_=load_fruit_rows(workbook)
        report=json.loads(Path(receipt).read_text())
        if (len(rows)!=74 or report["verified_original_workbook_sha256"]!=SOURCE_SHA256
                or not report["post_outcome_exploratory_not_confirmatory"]):
            raise ValueError("original source report mismatch")
        errors=[]
        for case in report["models"].values():
            excluded=set(case["excluded_source_excel_rows"])
            sample=[r for i,r in enumerate(rows,2) if i not in excluded]
            fitted,contrast=numeric_oracle(sample)
            if len(sample)!=case["n"]:
                raise ValueError("source support mismatch")
            errors.extend(abs(value-case["F"][k]) for k,value in fitted.items())
            errors.extend(abs(value-case["conditional_dense_minus_sparse_fruit_set_pp"][k])
                          for k,value in contrast.items())
        lo=[numeric_oracle([r for j,r in enumerate(rows,2) if j!=i])[0]["interaction"]
            for i in range(2,76)]
        target=report["leave_one_spike_out_interaction_F"]
        errors.extend([abs(target["min"]-min(lo)),
                       abs(target["median"]-statistics.median(lo)),
                       abs(target["max"]-max(lo))])
        baseline=report["models"]["all_74"]["F"]["interaction"]
        top=sorted(range(2,76),key=lambda i:abs(lo[i-2]-baseline),reverse=True)[:5]
        if top!=[entry["excel_row"] for entry in target["five_largest_abs_changes"]]:
            raise ValueError("source row influence ordering drifted")
        delta=max(errors)
        if delta>1e-8:
            raise ValueError("independent least-squares disagreement")
        return {"status":"INDEPENDENT_NUMPY_ORACLE_PASS",
                "original_74_rows_verified":True,
                "case_models_verified":len(report["models"]),
                "leave_one_out_models_verified":74,
                "maximum_absolute_F_or_contrast_difference":delta,
                "original_source_sha256":SOURCE_SHA256,
                "patch_level_inference_identified":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-zip",type=Path,required=True)
    p.add_argument("--audit-receipt",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(verify(args.source_zip,args.audit_receipt),sort_keys=True))


if __name__=="__main__":
    main()
