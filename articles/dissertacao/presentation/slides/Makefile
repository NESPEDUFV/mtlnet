# Build dos slides de defesa. O motor TEM que ser xelatex ou lualatex -- nesped.sty carrega
# fontspec sob esses dois; ver a nota sobre pdflatex em ../_preparacao/PLANO_FLUXO_DEFESA.md §11 (compila
# sem erro, mas título/sumário/specialframe saem sem fundo -- não é um drop-in seguro hoje,
# e este deck usa \autotocframe em toda seção).
#
# Builda em build/ (gitignored) e copia o main.pdf final para a raiz desta pasta.

ENGINE = xelatex
FLAGS  = -interaction=nonstopmode -halt-on-error

.PHONY: all check clean

# main.tex hoje não tem nenhuma citação -- o "-" antes do bibtex é necessário, não cosmético:
# sem ele, bibtex sai com erro (nada para processar) e derruba o make.
all:
	mkdir -p build
	$(ENGINE) $(FLAGS) -output-directory=build main.tex
	-bibtex build/main
	$(ENGINE) $(FLAGS) -output-directory=build main.tex
	$(ENGINE) $(FLAGS) -output-directory=build main.tex
	cp build/main.pdf main.pdf
	@echo "OK -- main.pdf"

# só valida que compila com 0 erros, não deixa PDF pela metade em caso de falha.
check:
	mkdir -p build
	@$(ENGINE) -interaction=nonstopmode -output-directory=build main.tex > /tmp/nesped_slides_check.log 2>&1; \
	if grep -q '^!' /tmp/nesped_slides_check.log; then \
		echo "FALHOU -- ver /tmp/nesped_slides_check.log"; grep -n '^!' /tmp/nesped_slides_check.log; exit 1; \
	else \
		echo "OK -- $$(grep 'Output written' /tmp/nesped_slides_check.log)"; \
	fi

clean:
	rm -rf build main.pdf
