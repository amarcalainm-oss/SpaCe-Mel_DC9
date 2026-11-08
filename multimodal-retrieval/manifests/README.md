# manifests/

Small tables written by the notebooks. All files here are **outputs**: they are (re)created by running the
notebooks, never edited by hand. The folder is empty until the notebooks are run.

| File | Written by | One row per | Key columns |
|---|---|---|---|
| `environment_versions.csv` | 00 | package | installed version |
| `inventory/inventory_summary.csv`, `inventory/inventory_files.csv` | 00 | section / file | image sizes, scale factors, µm per pixel |
| `file_presence.csv` | 00 | section | which of the 8 GEO file kinds exist |
| `geo_title_check.csv` | 01 | GSM | patients in GEO title vs section tokens in file names |
| `capture_areas.csv` | 01 | GSM (capture area) | sections, array size, scale factors, µm per pixel (grid), spot size in pixels |
| `skipped_samples.csv` | 01 | skipped section | reason |
| `load_report.csv` | 01 | section | matrix size, in-tissue spots, spots loaded, matrix scope |
| `barcode_overlap_check.csv` | 01 | pair of sections on one GSM | shared in-tissue barcodes |
| `reconciliation_spatial_reasoning.csv` | 01 | item | this manifest vs the spatial-reasoning documentation (sections, A2, capture-area sizes, gene panels, pixel size, spot totals, patients) |
| `tissue_sections.csv` | 01 | section | gsm, patient_id, in_paper_S1C, used_in_this_project, Table S1 clinical columns |
| `spots.csv.gz` | 01, QC columns by 02 | in-tissue spot | spot_uid, gsm, section_id, patient_id, barcode, array and pixel coordinates, x_um, y_um, hires_x, hires_y, region_label, QC metrics, qc_pass |
| `qc_summary.csv` | 02 | section | medians and pass rates |
| `fiducials_alignment_check.csv` | 03 | GSM | fraction of spots inside aligned_fiducials.jpg |
| `r2_published_reference.csv` | 04 | gene | values from Supplementary Tables S4/S5 |
| `r2_detection_by_section.csv` | 04 | section | % spots with CDK2/PRAME/SNX10/HHATL detected, co-detection, Spearman |
| `r3_marker_presence.csv`, `r3_evidence_levels.csv` | 04 | section / output | marker availability; evidence level of each immune output |
| `paired_spots/<GSM>_<section>/` | 05 | pair | `paired_spots.csv`, `patches/*.png`, `rna_counts.npz`, `rna_lognorm_cp10k.npz`, `rna_genes.csv`, `rna_rows.csv`, `pairing_checks.csv` |
| `paired_spots/paired_sections_summary.csv` | 05 | section | µm per pixel, patch sizes, number of pairs, genes per profile, minimum distance, all checks passed |

Identifier conventions: `gsm` = GEO sample = capture area; `section_id` = file token (e.g. `B38_2`);
`section_label` = name used by GEO titles and the paper (`B38.2`); `patient_id` = Table S1 "Visium ID" (`B38`);
`spot_uid` = `<gsm>:<barcode>`.