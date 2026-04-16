MAIN := main
ENGINE := pdflatex
BIBTEX := bibtex
LATEXMK := latexmk

.PHONY: all clean watch

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex refs.bib $(wildcard sections/*.tex) $(wildcard figures/*.pdf)
	$(LATEXMK) -pdf -bibtex -interaction=nonstopmode -halt-on-error $(MAIN).tex

watch:
	$(LATEXMK) -pdf -pvc -bibtex -interaction=nonstopmode $(MAIN).tex

clean:
	$(LATEXMK) -C
	rm -f *.bbl *.blg *.run.xml
