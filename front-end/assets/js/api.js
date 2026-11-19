/* ==================================================================
   Camada de comunicacao com o Back-end (API REST).
   Formatos usados aqui sao EXATAMENTE os documentados em
   docs/03-guia-integracao-front-end.md:
     - listagem  -> { total, dados: [...] }
     - item      -> { dados: {...} }
     - criacao   -> { mensagem, dados: { id } }
     - edicao    -> { mensagem, dados: {...} }
     - exclusao  -> { mensagem }
     - erro      -> { erro: "mensagem" }
   ================================================================== */

/* Se a API estiver servindo esta pagina (mesma porta 5000), usamos
   caminho relativo. Caso contrario (servidor estatico em outra porta),
   usamos o endereco completo da API. */
const API_BASE = (window.location.port === '5000')
  ? ''
  : 'http://127.0.0.1:5000';

async function apiRequisicao(metodo, caminho, corpo) {
  const opcoes = {
    method: metodo,
    headers: { 'Content-Type': 'application/json' },
  };
  if (corpo !== undefined && corpo !== null) {
    opcoes.body = JSON.stringify(corpo);
  }

  let resposta;
  try {
    resposta = await fetch(`${API_BASE}/api${caminho}`, opcoes);
  } catch (erro) {
    throw new Error(
      'Nao foi possivel conectar a API. Verifique se o Back-end esta rodando (iniciar.bat).'
    );
  }

  let dados = {};
  try {
    dados = await resposta.json();
  } catch (erro) {
    dados = {};
  }

  if (!resposta.ok) {
    // o back-end sempre devolve { erro: "..." } - conforme o guia
    throw new Error(dados.erro || `Erro ${resposta.status} ao chamar a API.`);
  }
  return dados;
}

const api = {
  painel: () => apiRequisicao('GET', '/painel/resumo'),
  login: (nome_usuario, senha) =>
    apiRequisicao('POST', '/auth/login', { nome_usuario, senha }),

  listar: (recurso, parametros = '') =>
    apiRequisicao('GET', `/${recurso}${parametros}`),
  buscar: (recurso, id) =>
    apiRequisicao('GET', `/${recurso}/${id}`),
  criar: (recurso, dados) =>
    apiRequisicao('POST', `/${recurso}`, dados),
  atualizar: (recurso, id, dados) =>
    apiRequisicao('PUT', `/${recurso}/${id}`, dados),
  excluir: (recurso, id) =>
    apiRequisicao('DELETE', `/${recurso}/${id}`),
};
