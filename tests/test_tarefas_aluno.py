"""TAREFA DO ALUNO -- os cinco testes que faltam para os >= 8 do entregavel.

Cada teste abaixo tem nome, docstring e um pytest.skip. Apague o skip, escreva o
corpo, e o teste passa a valer. Nenhum deles precisa de banco: os tres primeiros
rodam so contra o motor.
"""

from __future__ import annotations

from decimal import Decimal

import pytest


def test_regressao_numerica_contra_a_planilha(fluxos_golden):
    """Compara os seis indices com a aba SSB da Planilha_base.xlsx.

    Criterio do entregavel: abs(delta) <= 1E-6 por indice. Comece pelo inventario
    de referencia (Y = 200, F = 50, renovaveis = 115, nao renovaveis = 85) e
    escreva os seis valores esperados a mao antes de rodar -- se o teste passar
    de primeira sem voce saber o valor esperado, ele nao esta provando nada.
    """
    pytest.skip("TODO PASSO 5: escrever a regressao numerica")


def test_quantizacao_unica_no_final():
    """Mostra o erro duplo de arredondar no meio do calculo.

    Calcule ESI = EYR / ELR de duas formas: (a) quantizando EYR e ELR para seis
    casas antes de dividir; (b) dividindo em 28 digitos e quantizando so o ESI.
    Os dois resultados diferem -- e o motor usa (b). Prove a diferenca.
    """
    pytest.skip("TODO PASSO 5: provar o erro duplo do arredondamento intermediario")


def test_ordem_da_soma_com_magnitudes_divergentes():
    """A associatividade quebra quando as magnitudes divergem.

    Monte um inventario com um fluxo de 1E20 sej e outro de 1E-5 sej e some nas
    duas ordens possiveis. Explique, no corpo do teste, por que a precisao de 28
    digitos e o limite -- e por que ordenar o inventario e uma decisao de dominio.
    """
    pytest.skip("TODO PASSO 5: exercitar o limite de precisao")


def test_erro_de_dominio_responde_problem_json(cliente, corpo_golden):
    """Inventario sem fluxo renovavel deve sair 422 em application/problem+json.

    Hoje sai 500, porque o handler de FluxosInsuficientes nao existe -- note que
    o 404 e o 422 do framework JA saem no formato certo, pelos handlers do
    esqueleto: o que falta e so o erro de dominio. Feche o TODO PASSO 3 em
    app/main.py e depois assegure aqui: status 422, header content-type
    application/problem+json e os cinco campos da RFC 9457.
    """
    pytest.skip("TODO PASSO 3 + 5: handler de FluxosInsuficientes e este teste")


def test_campo_extra_no_corpo_da_requisicao_e_rejeitado(cliente, corpo_golden):
    """"energia_produto_jj" tem de morrer com 422, nao virar calculo incompleto.

    Hoje o CalculoRequestDTO nao declara extra="forbid": o campo desconhecido e
    ignorado e o typo passa silencioso, exatamente como na planilha. Feche o
    TODO PASSO 3 em app/api/v1/dto.py e prove aqui.
    """
    pytest.skip("TODO PASSO 3 + 5: extra=forbid no CalculoRequestDTO e este teste")
