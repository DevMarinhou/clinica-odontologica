"""Painel principal - resumo com as contagens para a tela inicial.

Fornece tudo que a home do front-end precisa exibir em uma unica
requisicao (totais, consultas de hoje, proximas consultas...).
"""
from flask import Blueprint, jsonify

from app import banco

bp = Blueprint('painel', __name__)

_SELECT_CONSULTA = """
SELECT c.id, c.data_hora, c.status,
       p.nome AS paciente_nome,
       d.nome AS dentista_nome,
       pr.nome AS procedimento_nome
FROM consultas c
JOIN pacientes p      ON p.id = c.paciente_id
JOIN dentistas d      ON d.id = c.dentista_id
JOIN procedimentos pr ON pr.id = c.procedimento_id
"""


def _contar(sql, params=()):
    linha = banco.consultar_um(sql, params)
    return int(list(linha.values())[0]) if linha else 0


@bp.get('/api/painel/resumo')
def resumo():
    """Devolve os indicadores do painel da clinica."""
    dados = {
        'totais': {
            'pacientes': _contar('SELECT COUNT(*) FROM pacientes'),
            'dentistas': _contar('SELECT COUNT(*) FROM dentistas'),
            'procedimentos': _contar('SELECT COUNT(*) FROM procedimentos'),
            'consultas': _contar('SELECT COUNT(*) FROM consultas'),
            'usuarios': _contar('SELECT COUNT(*) FROM usuarios'),
        },
        'consultas_hoje': _contar(
            'SELECT COUNT(*) FROM consultas WHERE DATE(data_hora) = CURDATE()'
        ),
        'consultas_pendentes': _contar(
            "SELECT COUNT(*) FROM consultas "
            "WHERE status IN ('agendada', 'confirmada')"
        ),
        'consultas_por_status': banco.consultar(
            'SELECT status, COUNT(*) AS quantidade '
            'FROM consultas GROUP BY status ORDER BY quantidade DESC'
        ),
        'faturamento_concluido': banco.consultar_um(
            'SELECT COALESCE(SUM(pr.preco), 0) AS total '
            'FROM consultas c '
            'JOIN procedimentos pr ON pr.id = c.procedimento_id '
            "WHERE c.status = 'concluida'"
        )['total'],
        'proximas_consultas': banco.consultar(
            _SELECT_CONSULTA
            + " WHERE c.data_hora >= NOW() "
              "AND c.status IN ('agendada', 'confirmada') "
            + 'ORDER BY c.data_hora ASC LIMIT 5'
        ),
    }
    return jsonify({'dados': dados})
