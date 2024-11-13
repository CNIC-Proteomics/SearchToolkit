# MZ_extractor

This program adds the intensities to the identification file from the mzML, reporting the ion isotopic distribution.

Usage:
```
python mz_extractor.py \
-i "tests/test1/msfragger/Jurkat_Fr3.tsv" \
-z "tests/test1/thermo_raw_parser/Jurkat_Fr3.mzML" \
-r "tests/test1/reporter_ion_isotopic.tsv" \
-o "tests/test1/mz_extractor"
```

```
python mz_extractor.py \
-i "tests/test1/msfragger/*.tsv" \
-z "tests/test1/thermo_raw_parser/*.mzML" \
-r "tests/test1/reporter_ion_isotopic.tsv" \
-o "tests/test1/add_quant"
```


Test the AnaDelVal patch
```
python mz_extractor.py \
-i "S:\U_Proteomica\UNIDAD\Softwares\jmrodriguezc\mz_extractor\tests\test2\RH_Heart_TMTHF_FR1WO_duplicate_SHIFTS_BestPSM_calibrated.tsv" \
-z "S:\U_Proteomica\UNIDAD\Softwares\jmrodriguezc\mz_extractor\tests\test2\RH_Heart_TMTHF_FR1WO_duplicate_SHIFTS_BestPSM_calibrated.mzML" \
-r "S:\U_Proteomica\UNIDAD\Softwares\jmrodriguezc\mz_extractor\tests\test2\XH338783_TMT10PLEX_noCORR.tsv" \
-o "S:\U_Proteomica\UNIDAD\Softwares\jmrodriguezc\mz_extractor\tests\test2" \
-p 10
```

-i "S:\U_Proteomica\UNIDAD\Softwares\jmrodriguezc\mz_extractor\tests\test2\RH_Heart_TMTHF_FR1WO_duplicate_SHIFTS_BestPSM_calibrated.tsv" -z "S:\U_Proteomica\UNIDAD\Softwares\jmrodriguezc\mz_extractor\tests\test2\RH_Heart_TMTHF_FR1WO_duplicate_SHIFTS_BestPSM_calibrated.mzML" -r "S:\U_Proteomica\UNIDAD\Softwares\jmrodriguezc\mz_extractor\tests\test2\XH338783_TMT10PLEX_noCORR.tsv" -o "S:\U_Proteomica\UNIDAD\Softwares\jmrodriguezc\mz_extractor\tests\test2" -p 10


<!--
## Include a specific path from an external repository in your own repository

1. Clone Your Main Repository:
```
git clone <main_repository_url>
git clone https://github.com/CNIC-Proteomics/add_quant.git
```
2. Add the Remote Repository:
```
git remote add external-repo <external_repository_url>
git remote add external-repo https://github.com/CNIC-Proteomics/iSanXoT.git
```
3. Fetch the External Repository:
Fetch the external repository to get its data, which includes the specific path you want:
```
git fetch external-repo
```
4. Merge the External Repository's Path:
Use the git read-tree command to merge the specific path from the external repository into your main repository. For example:

```
git read-tree --prefix=<submodule_path>/ -u external-repo/main-branch:<path_in_external_repo>
git read-tree --prefix=libs/ -u external-repo/master:app/resources/src/libs

```
5. Commit and Push Changes:
After merging the external path into your repository, commit the changes:
```
git commit -m "Added specific path from external repository"
git push
```
-->
