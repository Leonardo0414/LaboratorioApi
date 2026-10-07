"""TAREFA DO ALUNO -- os cinco testes que faltam para os >= 8 do entregavel.

Nenhum deles precisa de banco: os tres primeiros rodam so contra o motor; os
dois ultimos passam pela fronteira HTTP com o TestClient, sem servidor.
"""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal, localcontext

from app.dominio.motor_emergia import SEIS_CASAS, calcular_indices
from app.dominio.tipos import CategoriaFluxo, FluxoEmergetico


def test_regressao_numerica_contra_a_planilha(fluxos_golden):
    """Compara os seis indices com a aba SSB da Planilha_base.xlsx.

    Criterio do entregavel: abs(delta) <= 1E-6 por indice. Valores derivados a
    mao do inventario de referencia (R=100, N=50, MR=10, MN=20, SR=5, SN=15):
        Y    = R + N + M + S      = 200
        F    = M + S              = 50
        ren  = R + MR + SR        = 115
        nren = N + MN + SN        = 85
        EYR  = Y / F              = 4
        ELR  = nren / ren = 85/115 = 0.7391304347... -> 0.739130
        ESI  = EYR / ELR  = 460/85 = 5.4117647058... -> 5.411765
        EII  = ELR / EYR  = 85/460 = 0.1847826086... -> 0.184783
        %R   = ren / Y * 100      = 57.5
    """
    esperado = {
        "y": Decimal("200.000000"),
        "eyr": Decimal("4.000000"),
        "elr": Decimal("0.739130"),
        "esi": Decimal("5.411765"),
        "eii": Decimal("0.184783"),
        "percentual_r": Decimal("57.500000"),
    }
    tolerancia = Decimal("1E-6")
    indices = calcular_indices(fluxos_golden, Decimal("1000"))
    for nome, valor in esperado.items():
        obtido = getattr(indices, nome)
        assert abs(obtido - valor) <= tolerancia, f"{nome}: {obtido} != {valor}"


def test_quantizacao_unica_no_final(fluxos_golden):
    """Mostra o erro duplo de arredondar no meio do calculo.

    ESI = EYR / ELR com o inventario de referencia: EYR = 4, ELR = 85/115.
    (a) quantiza EYR e ELR para seis casas ANTES de dividir;
    (b) divide em 28 digitos e quantiza so o ESI -- e o que o motor faz.
    """
    with localcontext() as ctx:
        ctx.prec = 28
        ctx.rounding = ROUND_HALF_EVEN
        eyr = Decimal(200) / Decimal(50)
        elr = Decimal(85) / Decimal(115)

        # (a) arredondamento intermediario: o erro de ELR (0.739130 em vez de
        # 0.7391304347...) entra na divisao e e amplificado por ela
        esi_a = (eyr.quantize(SEIS_CASAS) / elr.quantize(SEIS_CASAS)).quantize(SEIS_CASAS)
        # (b) quantizacao unica, no final
        esi_b = (eyr / elr).quantize(SEIS_CASAS)

    assert esi_a != esi_b
    assert esi_a == Decimal("5.411768")        # 4 / 0.739130 = 5.41176787...
    assert esi_b == Decimal("5.411765")        # 460 / 85     = 5.41176470...
    assert abs(esi_a - esi_b) == Decimal("3E-6")   # tres vezes a tolerancia do entregavel

    # O motor usa (b): o ESI dele coincide com a quantizacao unica
    assert calcular_indices(fluxos_golden, Decimal("1000")).esi == esi_b


def test_ordem_da_soma_com_magnitudes_divergentes():
    """A associatividade quebra quando as magnitudes divergem.

    1E20 + 1E-5 exige 26 digitos significativos (21 antes da virgula, 5
    depois) e cabe nos 28 do contexto: a soma e exata em qualquer ordem.
    Com 1E25 no lugar de 1E20 a soma exata precisa de 31 digitos e NAO cabe:
    cada soma parcial e arredondada para 28 digitos, e uma parcela pequena
    somada a um total ja grande e descartada antes de ter chance de se
    acumular. A partir dai o resultado depende da ORDEM dos termos.

    Por isso a precisao de 28 e o limite: ela garante exatidao enquanto a
    razao entre o maior e o menor fluxo do inventario couber nessas casas.
    Alem disso a ordem de soma passa a fazer parte do resultado -- e decidir
    essa ordem (somar os pequenos primeiro, ou impor um limite de magnitude
    ao inventario) e regra do DOMINIO, nao do banco nem da rota, porque so o
    dominio sabe o que um sej significa e quanto erro e aceitavel.
    """
    grande = Decimal("1E20")
    pequeno = Decimal("1E-5")
    mil_pequenos = [pequeno] * 1000             # somados: 0.01

    with localcontext() as ctx:
        ctx.prec = 28
        ctx.rounding = ROUND_HALF_EVEN

        # Dentro do limite (25 ordens de grandeza): a ordem nao importa.
        assert grande + pequeno == pequeno + grande
        assert grande + pequeno == Decimal("100000000000000000000.00001")
        um_a_um = grande
        for p in mil_pequenos:
            um_a_um += p
        pequenos_primeiro = grande + sum(mil_pequenos)
        assert um_a_um == pequenos_primeiro == Decimal("100000000000000000000.01")

        # Fora do limite (30 ordens de grandeza): a ordem decide o resultado.
        maior = Decimal("1E25")
        um_a_um = maior
        for p in mil_pequenos:
            um_a_um += p                        # cada passo arredonda e perde 1E-5
        pequenos_primeiro = maior + sum(mil_pequenos)   # 1E25 + 0.01 cabe em 28 digitos
        assert um_a_um == maior                 # os mil fluxos sumiram
        assert pequenos_primeiro == Decimal("10000000000000000000000000.01")
        assert um_a_um != pequenos_primeiro     # mesma entrada, somas diferentes

    # O motor, dentro do limite, da o mesmo Y com o inventario em qualquer ordem
    # (os demais fluxos mantem EYR/ELR/ESI em magnitude quantizavel em 28 digitos).
    fluxos = [FluxoEmergetico("sol", CategoriaFluxo.R, grande),
              FluxoEmergetico("semente", CategoriaFluxo.MR, pequeno),
              FluxoEmergetico("solo", CategoriaFluxo.N, Decimal("1E19")),
              FluxoEmergetico("diesel", CategoriaFluxo.MN, Decimal("1E18"))]
    y1 = calcular_indices(fluxos, Decimal("1000")).y
    y2 = calcular_indices(list(reversed(fluxos)), Decimal("1000")).y
    assert y1 == y2 == Decimal("111000000000000000000.000010")


def test_erro_de_dominio_responde_problem_json(cliente, corpo_golden):
    """Inventario sem fluxo renovavel deve sair 422 em application/problem+json."""
    corpo_golden["fluxos"] = [f for f in corpo_golden["fluxos"]
                              if f["categoria"] in ("N", "MN")]
    r = cliente.post("/v1/safras/42/calculos", json=corpo_golden)
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")
    corpo = r.json()
    for campo in ("type", "title", "status", "detail", "instance"):
        assert campo in corpo
    assert corpo["status"] == 422
    assert corpo["type"].endswith("/fluxos-insuficientes")
    assert corpo["instance"] == "/v1/safras/42/calculos"
    assert "ELR" in corpo["detail"]


def test_campo_extra_no_corpo_da_requisicao_e_rejeitado(cliente, corpo_golden):
    """"energia_produto_jj" tem de morrer com 422, nao virar calculo incompleto."""
    corpo_golden["energia_produto_jj"] = "1000"      # typo ao lado do campo certo
    r = cliente.post("/v1/safras/42/calculos", json=corpo_golden)
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")
    campos = {e["campo"] for e in r.json()["erros"]}
    assert "body.energia_produto_jj" in campos

    # O typo NO LUGAR do campo certo tambem morre: o obrigatorio esta ausente.
    del corpo_golden["energia_produto_j"]
    r = cliente.post("/v1/safras/42/calculos", json=corpo_golden)
    assert r.status_code == 422
