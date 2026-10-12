"""AUT-35a: reproduce the line-numbered text extraction that the L-numbers in
70_massivesteps_validation.md refer to.

The paper text itself is NOT committed to this repository. This script regenerates
the extraction from the published PDF so that every "L<n>" citation in the report is
checkable, without redistributing a third party's manuscript.

Usage:
  curl -sSL -o ms_v3.pdf https://arxiv.org/pdf/2505.11239v3
  python3 aut35a_extract_pdf_text.py ms_v3.pdf > ms_v3.txt
  grep -n "non-consecutive" ms_v3.txt

Extraction backend: pypdfium2 get_text_range(), page order, pages joined by a form
feed. Any other extractor will renumber the lines.
"""
import sys
import pypdfium2

doc = pypdfium2.PdfDocument(sys.argv[1])
pages = [doc[i].get_textpage().get_text_range() for i in range(len(doc))]
sys.stdout.write("\n\f\n".join(pages))
