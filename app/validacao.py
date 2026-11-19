"""Validacao dos dados recebidos pelo cliente (front-end).

Toda entrada que vem de fora passa por aqui antes de chegar ao banco.
O objetivo e devolver mensagens claras (HTTP 400) em vez de deixar o
MySQL reclamar com mensagens tecnicas.
"""
import re
from datetime import date, datetime

STATUS_CONSULTA = ('agendada', 'confirmada', 'em_andamento',
                   'concluida', 'cancelada')
PERFIS_USUARIO = ('admin', 'recepcao', 'dentista', 'financeiro')


class ErroValidacao(Exception):
    """Erro de entrada do cliente. Vira resposta HTTP 400."""


def exigir_json(dados):
    if not isinstance(dados, dict):
        raise ErroValidacao(
            'Corpo da requisicao invalido. Envie um JSON no formato {chave: valor}.'
        )


def exigir_campos(dados, campos):
    """Garante que os campos obrigatorios estao presentes e preenchidos."""
    exigir_json(dados)
    faltando = [
        campo for campo in campos
        if dados.get(campo) is None or str(dados.get(campo)).strip() == ''
    ]
    if faltando:
        raise ErroValidacao(
            'Campo(s) obrigatorio(s): ' + ', '.join(faltando) + '.'
        )


def texto(dados, campo, tamanho_max, obrigatorio=True, padrao=None):
    """Retorna o campo como string limpa, validando o tamanho."""
    valor = dados.get(campo)
    if valor is None or str(valor).strip() == '':
        if obrigatorio:
            raise ErroValidacao(f'Campo "{campo}" e obrigatorio.')
        return padrao
    valor = str(valor).strip()
    if len(valor) > tamanho_max:
        raise ErroValidacao(
            f'Campo "{campo}" deve ter no maximo {tamanho_max} caracteres '
            f'(recebido: {len(valor)}).'
        )
    return valor


def validar_cpf(valor):
    """Valida CPF com todos os digitos verificadores e devolve formatado."""
    digitos = re.sub(r'\D', '', str(valor or ''))
    if len(digitos) != 11 or digitos == digitos[0] * 11:
        raise ErroValidacao('CPF invalido. Use o formato 000.000.000-00.')

    def parcial(numeros):
        soma = sum(n * (len(numeros) + 1 - i) for i, n in enumerate(numeros))
        resto = (soma * 10) % 11
        return 0 if resto == 10 else resto

    base = [int(c) for c in digitos[:9]]
    d1 = parcial(base)
    d2 = parcial(base + [d1])
    if d1 != int(digitos[9]) or d2 != int(digitos[10]):
        raise ErroValidacao('CPF invalido: digitos verificadores nao conferem.')

    return f'{digitos[0:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:11]}'


def validar_email(valor):
    """Valida o formato do e-mail. Vazio retorna None (coluna aceita NULL)."""
    if valor is None or str(valor).strip() == '':
        return None
    email = str(valor).strip().lower()
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]{2,}', email):
        raise ErroValidacao(f'E-mail invalido: "{valor}".')
    if len(email) > 100:
        raise ErroValidacao('E-mail deve ter no maximo 100 caracteres.')
    return email


def validar_data(valor):
    """Aceita AAAA-MM-DD ou DD/MM/AAAA e devolve um objeto date."""
    texto_valor = str(valor or '').strip()
    for formato in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(texto_valor, formato).date()
        except ValueError:
            continue
    raise ErroValidacao(
        f'Data invalida: "{valor}". Use o formato AAAA-MM-DD.'
    )


def validar_data_hora(valor):
    """Aceita AAAA-MM-DDTHH:MM(:SS) ou AAAA-MM-DD HH:MM e devolve datetime."""
    texto_valor = str(valor or '').strip().replace('T', ' ')
    for formato in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M'):
        try:
            return datetime.strptime(texto_valor, formato)
        except ValueError:
            continue
    raise ErroValidacao(
        f'Data/hora invalida: "{valor}". Use o formato AAAA-MM-DD HH:MM.'
    )


def validar_preco(valor):
    """Valida valor monetario e devolve com 2 casas decimais."""
    try:
        preco = float(str(valor).replace(',', '.'))
    except (TypeError, ValueError):
        raise ErroValidacao(f'Preco invalido: "{valor}".')
    if preco < 0:
        raise ErroValidacao('Preco nao pode ser negativo.')
    return round(preco, 2)


def validar_inteiro(valor, campo, minimo=0):
    """Valida numero inteiro (ids, duracao, flag ativo)."""
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ErroValidacao(f'Campo "{campo}" deve ser um numero inteiro.')
    if numero < minimo:
        raise ErroValidacao(f'Campo "{campo}" deve ser maior ou igual a {minimo}.')
    return numero


def validar_status(valor, obrigatorio=False):
    """Valida o status da consulta contra a lista permitida."""
    status = str(valor or '').strip().lower()
    if not status:
        if obrigatorio:
            raise ErroValidacao('Campo "status" e obrigatorio.')
        return None
    if status not in STATUS_CONSULTA:
        raise ErroValidacao(
            'Status invalido. Use um de: ' + ', '.join(STATUS_CONSULTA) + '.'
        )
    return status


def validar_perfil(valor, padrao='recepcao'):
    """Valida o perfil do usuario."""
    perfil = str(valor or '').strip().lower() or padrao
    if perfil not in PERFIS_USUARIO:
        raise ErroValidacao(
            'Perfil invalido. Use um de: ' + ', '.join(PERFIS_USUARIO) + '.'
        )
    return perfil


def validar_ativo(valor, padrao=1):
    """Converte true/false ou 1/0 em TINYINT."""
    if valor is None:
        return padrao
    if isinstance(valor, bool):
        return 1 if valor else 0
    return validar_inteiro(valor, 'ativo', minimo=0)


def validar_senha(valor, tamanho_min=6):
    """Exige senha com tamanho minimo (nunca guarda texto puro, so hash)."""
    senha = str(valor or '')
    if len(senha) < tamanho_min:
        raise ErroValidacao(
            f'Senha deve ter pelo menos {tamanho_min} caracteres.'
        )
    if len(senha) > 128:
        raise ErroValidacao('Senha deve ter no maximo 128 caracteres.')
    return senha
