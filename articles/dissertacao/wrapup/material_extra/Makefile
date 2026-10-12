# O volume de material extra, construido a partir da wrapup.
#
# As tabelas e a classe continuam vindo de ../../src, via TEXINPUTS: os apendices leem
# tables/... e o preambulo da dissertacao, e duplicar esses arquivos criaria duas copias que
# divergem em silencio. TEXINPUTS resolve sem copiar.
SRC   := ../../src
UTILS := ../../src_utils
BUILD := $(UTILS)/latexbuild.sh

extra:
	@mkdir -p build/main_extra-aux/chapters   # \include escreve um .aux por capitulo
	@TEXINPUTS=".//:$(abspath $(SRC))//:" BSTINPUTS=".//:$(abspath $(SRC))//:" \
	  BIBINPUTS=".//:$(abspath $(SRC))//:" $(BUILD) main_extra main_extra.tex

clean:
	@rm -rf build
