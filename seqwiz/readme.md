![SeqWiz LOGO](logo.png)  
SeqWiz: a modularized toolkit for next-generation protein sequence database management and analysis
* * *

*   ### Installation
    
    **(1) . Required environments:**
    
    Python 3.x, with pip and requests
    
    **(2). Install Biopython for predicting physicochemical properties**
    
    ```sh
    >>> pip install biopython
    ```
    
    \*Recommended version: 1.7.x
    
    See: [https://biopython.org/wiki/Download](https://biopython.org/wiki/Download )
    
    (3). Install wxPython for GUI supports
    
    Recommended version: 4.x  
    For Windows:
    ```sh
    >>> pip install -U wxPython
    ```
    For Ubuntu 20.04:
    ```sh
    >>> pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython
    #for libsdl supports, if needed
    >>> sudo apt-get install libsdl2-2.0  
    >>> sudo apt-get install libsdl2-dev
    ```
    \*For other Linux distributions, please find the correct versions from: [https://extras.wxpython.org/wxPython4/extras/linux/](https://extras.wxpython.org/wxPython4/extras/linux/)
    See: [https://www.wxpython.org/pages/downloads/](https://www.wxpython.org/pages/downloads/)
    
*   ### Development and testing environments
    
    (1). SeqWiz was developed under Windows OS:
    Windows 7 Ultimate, 64bit; Python 3.8.10; Biopython 1.79; wxPython 4.1.1
    GUI snapshot for Windows:
    ![](windows.png)
    (2). SeqWIz was aslo tested under Ubuntu OS:
    ubuntu-20.04.2.0-desktop-amd64; Python 3.8.10; Biopython 1.79; wxPython 4.1.1
    GUI snapshot for Ubuntu:
    ![](ubuntu.png)
*   ### Functionalities
    
    |App name|Class|Functions|Note|
    |------|------|------|------|
    |UpSpecies|Core|Search or view taxonomy ID|Based on UniProt|
    |UpRetrieval|Core|Download species specific sequences and annotations, create structured database|Based on UniProt|
    |UpConvert|Core|Convert FASTA from UniProt to PEFF or SQPD|Based on UniProt|
    |CheckSeq|Core|Check the format of FASTA, PEFF, SQPD, SET or PEPLIS|\*PEPLIS: a list of peptide sequence|
    |DbManage|Core|Create structured database from non-UniProt sequences||
    |SeqConvert|Core|Simple format converter for non-UniProt sequences||
    |SeqFilter|Core|Sequence filter to generate a SET list from SQPD||
    |SeqDecoy|Core|Generate decoy FASTA sequences||
    |MatureSeq|Core|Generate mature forms of protein sequences|Based on UniProt annotations|
    |SepFinder|Core|Predict sORF and SEPs from transcript sequences||
    |SeqAnnotate|Additional|Sequence statistics for singular or grouped residues; calculation or prediciton of physicochemical properties, including: isoelectric point, physilogical charge, reduced molar extinction, cystines molar extinction, aromaticity, instability and grand average of hydropathy.|\*Require the biopython package|
    |TabFilter|Additional|Table filter to generate a SET list|\*Recommend to use the result table from SeqAnnotate|
    |MotifCount|Additional|Motif count||
    |SeqWindow|Additional|Sequence window extraction from a position table (for a list of sites or peptides)||
    
*   ### Usage
    
    (1). CMD usage
    
    Each tool of SeqWiz is designed with standard CLI interface, with self-describing arguments. Use the common "-h" flag to show the help in CLI:
    ```sh
    python {script_name}.py -h
    ```
    (2). GUI usage
    
    SeqWiz also provides a GUI-to-CLI interface to run the tools.
    Step1: Start with the index window to show the list of tools.
    Step 2: Select the tool in the APP list and lanuch it
    Step 3: Set the parameters as needed
    Step 4: Click the "Assemble" button to check input and generate CMDs
    Step 5: Click the "Run" button to stat the mission

*   ### Practical examples
    
    (1). To create mature sequences for mouse proteins
    Step 1: change to the "core" directory:
    ```sh
    ./seqwiz/core/
    ```
    Step 2: find the taxonomy ID
    ```sh
    >>> python UpSpecies.py -m search -s Mouse -k E
    ```
    Step 3: download sequences and annotations
    ```sh
    >>> python UpRetrieval.py -t 10090 -s -a
    ```
    Step 4: generate mature sequences in FASTA format
    ```sh
    >>> python MatureSeq.py ../seqdbs/Uniprot/MOUSE_10090/2021_03/next/sqpd/SQPD.db -f
    ```
    Step 5: check the result file
    ```sh
    ./seqdbs/uniprot/MOUSE_10090/2021_03/classic/fasta/Single_mature.fasta
    ```
    (2). To predict SEPs derived from lncRNA transcripts (via GUI)
    Step 1: open the index window, choose the "SepFinder" in the APP list and launch the APP
    ![](example2_1.png)
    Step 2: choose the transcript FASTA file:
    ![](example2_2.png)
    Step 3: Choose the parsing rule
    Step 4: Choose the codon level
    Step 5: click "?" to show the help pop-up for initial codon level
    Step 6: click the "Assemble" to check input and generate CMDs
    Step 7: click the "Run" to stat the ruuning of this mission
    (3). To generat subsets and retrieving sequences
    Step 1: change to the "core" directory:
    ```sh
    ./seqwiz/core/
    ```
    Step 2: generate a SET of reference proteome
    ```sh
    >>> python SeqFilter.py ../seqdbs/uniprot/MOUSE_10090/2021_03/next/sqpd/SQPD.db -f Proteomes -e " " -t exact -l proteome -m remove
    ```
    Step 3: generate a SET of small proteins, based on reference proteome
    ```sh
    >>> python ../adds/TabFilter.py ../seqdbs/uniprot/MOUSE_10090/2021_03/classic/table/properties.tsv -c 2 -l small -e ¡°<200¡± -t numeric -n ¡°<max¡± -i intersection -r ../seqdbs/uniprot/MOUSE_10090/2021_03/next/sets/SQPD_filter_proteome.json
    ```
    Step 4: generate a SET of sequences with a speific motif, based on small SET
    ```sh
    >>> python SeqFilter.py ../seqdbs/uniprot/MOUSE_10090/2021_03/next/sqpd/SQPD.db -f sequence -e "N[^P][S|T|C|V]" -t pattern -i intersection -r -l motif ../seqdbs/uniprot/MOUSE_10090/2021_03/next/sets/properties_filter_small.json
    ```
    Step 5: convert all of the SETs into classic FASTA files
    ```sh
    >>> python SeqConvert.py ../seqdbs/uniprot/MOUSE_10090/2021_03/next/sets/SQPD_filter_proteome.json -t set2fasta -l proteome
    
    >>> python SeqConvert.py ../seqdbs/uniprot/MOUSE_10090/2021_03/next/sets/properties_filter_small.json -t set2fasta -l small
    
    >>> python SeqConvert.py ../seqdbs/uniprot/MOUSE_10090/2021_03/next/sets/SQPD_filter_motif.json -t set2fasta -l motif
    ```
*   ### License
    
    This project follows the GNU General Public License (version: 3.0).
    See: [https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html)