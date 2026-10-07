"""PASSO 4 do laboratorio: a rota-armadilha.

Higiene: apague este arquivo ao final da aula, ou mantenha-o num branch de
demonstracao. Codigo que ensina errado nao fica em main.
"""

from __future__ import annotations

import time

from fastapi import APIRouter

router = APIRouter(prefix="/v1/demo", tags=["armadilha"])


@router.get("/travada")
async def travada():
    # async + chamada BLOQUEANTE: o event loop inteiro para aqui
    time.sleep(10)
    return {"ok": True}
    # TODO PASSO 4: com o servidor rodando, chame esta rota num terminal e
    # imediatamente abra /docs no navegador. O Swagger nao carrega -- nada carrega.
    # Corrija de UMA das duas formas e repita a chamada:
    #   (a) trocar "async def travada" por "def travada"       -> vai para o thread pool
    #   (b) trocar time.sleep(10) por "await asyncio.sleep(10)" -> devolve o loop
    # Explique, em uma linha no seu PR, por que as duas funcionam.
