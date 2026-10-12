# Estado — root_migration

**Última atualização:** 2026-08-20

## Onde estamos

Estudo criado com o inventário levantado e as dependências verificadas. **Nada foi movido.**

## Feito

- [x] inventário dos doze irmãos, com tamanhos
- [x] as cinco dependências reais mapeadas e verificadas (ver [`STUDY.md`](STUDY.md))
- [x] dados primários já desacoplados para a fonte única (19-08)

## Próximo

A decisão que governa todas as outras: **o que fazer com a suíte de equivalência.** Ela é o que prova
que o porte reproduz a referência, e importa o repo antigo por caminho absoluto. Três saídas:

1. manter um checkout fixado da referência num caminho estável e re-apontar os seis arquivos;
2. congelar a evidência que os testes produzem hoje e marcá-los como históricos;
3. um híbrido — congelar a evidência **e** manter o checkout enquanto a tarefa de avaliação contra a
   dissertação não fechar.

## Bloqueios

- O estudo [`improvements`](../improvements/STUDY.md) está aberto e vai produzir comparações. Mexer
  na árvore antes disso é risco sem ganho.
