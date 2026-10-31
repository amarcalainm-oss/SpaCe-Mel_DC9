1. What are the paper's primary biological research question and its rationale?
State what the authors wanted to learn about nevus-to-melanoma transition; distinguish biological aims from methods.

They wanted to see the transciptional and microenvironmental changes that happen in the transtion from nevus to melanoma. They are interested in these two cells, since nevus and melanoma hrbor mutations in the same genes (BRAF or NRAS) that activate the MAPK signaling pathway. Earlier works mainly focused on bulk RNA sequencing, or only analyzed limited gene subsets, lacks spatial context or focused on advanced-stage melanoma only instead of earlier stages too. This study tries to fill these gaps being specifcially focused on the transcirptional reprogramming and the alterations in the tumour microenvironment. 

2. What biological material was studied, and what is the correct unit of independence?
Identify tissue states, sampling structure, Visium spots versus specimens/patients, and use of adjacent sections.

18 lesions were studied from patient (unit of independence) ranging 17-72 and melanoma stages T1a-T3b. The resulting dataset contained 39,481 spots (unit of measurement - 55 microm containing 5-10 cells each) covering up to 18,072 genes. The approach focuses on intradermal nevus to invasive melanoma (and does not detail mmuch on junctional nevus into melanoma in situ). Nevus-melanoma contents were evaluated based on the H&E sections with immunohistemichal staining for SOX10, PRAME and p16. 15 trancriptomical profiles were indentified after deconvolution and to each a cell type was assigned (based on publicly available profiles). A single cell type was assigned to each spot and for 80.5% of those spots at least 40% was the assigned cell type of that specific spot. The FFPE blocks of skin tissue were sectioned at 5 microm tichkness for Visium and from the same block a consecutive slice (4microm) of the tissue sample was taken for IMC.

3. Why did the authors combine Visium with imaging mass cytometry?
Specify what each modality measures and which claims were supported by RNA versus protein evidence.

Visium measures thespatially resolved gene expression (RNA) across ~18,000 genes at spot level, explaining what genes are being expressed and where in the tissue, while IMC focuses on the protein levels at pixel(single cell) resolution (tells us what proteins are present and where). However the protain does not always follow from the gene transcription (RNA present but protein not), so RNA itself is not enough to deny/confirm the cell type. Therefore here IMC was used to validate the Visium findings confirming actual markers and providing single-cell spatial resolution.

4. How were nevus, melanoma, and other tissue regions identified or annotated?
Locate the description of histopathology/region labels and establish whether per-spot labels are publicly available.

Before computation by means of histopathological annotation by a dedicated dermatologist who revieved the stained tissue samples. As for the computation, deconvolution was done (STdeconvolve) to distinguish the different transcriptomical regions that were assigned a cell type by verification of publicly available data. It was verified that the location of the nevus/melanoma spots corresponded to the histopathological annotation. For the melanoma signatures two types were identifeid M1 and M2, however since M2 tended to have low spot purity, the study manly focused on M1. Per-spot labels are not publicly available, the deconvolution has to be ran (GSE298774).

5. What preprocessing and analytical methods did the authors use?
Include filtering, normalization, cell-type deconvolution, differential expression, immune infiltration, spatial analyses, pseudotime and ligand-receptor analysis where applicable. Reference scripts.

Formalin-fixed, paraffin embedded (FFPE) tissue sample blocks were used from a pathogoly archive, filtered by the ones that mentioned nevus adjacent to melanoma component and verified by a dedicated dermatologist who revised H&E, SOX10, PRAME, p16 staining to identify the most representative samples containing clear characteristics and morphologic distinction. For Visium the FFPE blocks were sectioned. Spots in the resulting slides had a diameter of 55microm and each spot contained 5 to 10 cells (deconvolution is needed). The final libraries were sequenced with NovaSeq 6000. In the end with the Visium image, H&E image and processed data with Rpackage semla, spots were obtained with more than 500 genes retained as well as spots with less than 30% mithorcondrial counts.

Deconvolution (Deconvolute_Visium.md) was done with the R package STdeconvolve (reference free method). To find the right number of K (number of topics) the function fitLDA was used with K raning from 10 to 20. To assign a cell type to a defined topic prvious literature was used. High Pearson correlation between cell type signiture and topic indicated a specific cell type was found. All spots surrounding a spot of a specific cell type were identified to analyze the neighbors and the distance epthelial cells to the nearest melanoma spots was also calculated. 

DEGs (DEGs_Visium_NevusTumor.md) are genes that are significantly differentially expressed between nevus-dominated spots and melanoma-dominated spots, to identify them a negative binomial model was implemented. For thresholds, |log2FC| ≥ 1, Padj ≤ 0.05, expressed in >25% of spots was defined. For approx 250 genes DEGs showed an on/off difference (expressions being almost exclusive for nevus or melanoma). DEGs were also ivestigated patient-to-patient. External data sources were used to verify DEGs.

To see which pathways are overrepresented in up and downregulated DEGs enrichment analysis (DEGs_OnOff_Enrichment.md) was performed using the Reactome and  KEGG databases.

Cell-cycle was also analyzed (CellCycle_estimation.md) on spots of >50% purity and percentage for three pahses were calculated. 

Ligand-receptor interaction analysis (SpatialDM_ExpressionBased_withFiltering.md) was performed on close enough cells, to draw conclusions on the communication of nevus and melanoma cells. 

Immune cells were approximated by using functions from the semla R package (Immune_infiltration_IC1_Franken.md).

For imaging mass cytometry a consecutive slice of the tissue sample was obtained and a custom panel was used targeting structural and cell-defining markers. Data was stored as MCD and txt files and used for pixel-based data analysis. The poor quality image markers were excluded.


6. What are the three most important biological findings?
For each, give the evidence and figure/table number. Consider proliferation/metabolic adaptation, melanocytic programs and microenvironment remodeling.

By enrichment analysis it was found that in melanoma upregulated pathways included those that support increased cell cycle and help manage heightened metabolic/proteotoxic stress. (Figure 3A and 3B) The increased proliferation in melanoma was reflected by cell-cycle phase too with melanoma mainly being in S-phase and G2-M-phase, while nevus cells in G1-phase, both fitting their growth rate (Fig 3c and 3d).

The enrichment analysis also identified the upregulation of developmental biology pathways regulated by the MITF transcription factor, during transition from nevus to melanoma. Verified by previously published literature, melanoma cells showed relatively higher melanocytic transcriptional signature scores compared to nevus cells, representing a shift from a neural crest-like transitory signature in nevus to a more melanocytic signature in melanoma (Fig 3E-I). MITF expression itself did not increase even though many of its target genes did, suggesting posttranslational regulation or the influence of other transcription factors.

ST and IMC was combined to identify immune cells in the melanoma microenvironment to spatially map levels of 43 immune and microenvironmental proteins (Fig 5a and 5b). ST revealed two immune cell signatures one being near melanoma containing multiple cells and one near fibroblast and mainly comprised of plasma cells. Meanwhile IMC verified that the immune cell population around the tumor included multiple immune cell types, while in contrast nevus tissue had almost exclusively M2-like macrophages. Other microenvironmental findings included that in pathways analysis there was an enrichment of antigen-presenting genes promoting antigen presentation in T lymphocytes. Moreover shifts in expression of genes linked to extracellular matrix organizations have been found (changes in expression of specific ECM proteins in the transition of melanoma and integrins). Some of these genes have been already associated with melanoma. Other than that melanoma cells were characterized by upregulation of ECM degradation genes. Moreover, deconvolution identified different signatures for fibroblasts and keratinocytes (Fig 4a and 4b).

7. What did the authors report about immune cells around nevi versus melanoma?
Differentiate observation, inferred cell identity and validated protein marker evidence; mention macrophage and T-cell patterns.

ST found two immune signitures, IC1 near melanoma containing multiple cell types, while IC2 was near fibroblasts throught the dermis mainly comprised of plasma cells. There was a big contrast in IMC imaging too, it revealed immune cell population around the tumors included multple immune cell types (like T cells, CD4, CD8), while inside there were only a few immune cells, and in nevi the only immune cells present were macrophages (Fig 5B and 5D) The macropahges in the nevus also differed from the ones around the tumor cells: the ones in nevi where M2-like (immunosurppressive nature) while the one snear tumor additionally contained CXCL10 macrophages, which are M1-like inflammatory and can attract T-cells. This observation could point to local immune activation in the melanoma region.

8. Which spatial questions have already been investigated?
Look explicitly for neighborhood/distance analyses, deconvolution, spatial ligand-receptor work and pseudotime in both the paper and code repository.

To analyze the cell types neighboring a specific cell type, all surrouding spots around a region were identified mainly to characterize the immune microenvironment around tumor vs nevus regions. Minimal distances were calculated for epithelial cells to the nearest melanoma spots (Pythagorean theorem). Deconvolution spatially maps cell type composition across the tissue which enables spatial comparisons. It was done for the ST spots since all contained cells ranging from 5 to 10 (STdeconvolve). Ligand-receptor analysis was performed for each patient separately (SpatialDM). Pseudotime is not specifically included in the paper, but the analysis was probably porformed (the scripts are icnluded in the repository - PseudoTime_NevusTumor.md), it was likely used as an exploratory/supplementary step.


9. What are the main limits of this study for new computational work?
Address cross-sectional sampling (not longitudinal proof of progression), spot-level resolution, patient/slide dependence, annotation quality and variation across samples. 

