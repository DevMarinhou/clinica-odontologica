/* ==================================================================
   CRUD de Procedimentos (catalogo de servicos)
   Endpoints: GET|POST /api/procedimentos ,
              GET|PUT|DELETE /api/procedimentos/<id>
   Busca: GET /api/procedimentos?busca=
   ================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  if (!layout.inicializar('procedimentos', 'Procedimentos',
    'Catalogo de servicos com preco e duracao')) return;

  const corpoTabela = document.getElementById('corpo-tabela');
  const campoBusca = document.getElementById('campo-busca');
  const formulario = document.getElementById('formulario-procedimento');
  const modal = bootstrap.Modal.getOrCreateInstance(
    document.getElementById('modal-procedimento'));
  const tituloModal = document.getElementById('titulo-modal');
  let idEdicao = null;

  async function carregar() {
    try {
      const termo = campoBusca.value.trim();
      const parametros = termo ? `?busca=${encodeURIComponent(termo)}` : '';
      const resposta = await api.listar('procedimentos', parametros);
      renderizar(resposta.dados, resposta.total);
    } catch (erro) {
      layout.aviso(erro.message, 'danger');
    }
  }

  function renderizar(dados, total) {
    document.getElementById('total-registros').textContent = total;
    if (!dados || !dados.length) {
      corpoTabela.innerHTML = `<tr><td colspan="5">
        <div class="empty-state"><i class="bi bi-inbox"></i>
        Nenhum procedimento encontrado com o filtro informado.</div></td></tr>`;
      return;
    }
    corpoTabela.innerHTML = dados.map((procedimento) => `
      <tr>
        <td>
          <strong>${layout.esc(procedimento.nome)}</strong>
          <div class="text-secondary small">${layout.esc(procedimento.descricao || '')}</div>
        </td>
        <td class="fw-semibold">${layout.moeda(procedimento.preco)}</td>
        <td>${procedimento.duracao_minutos} min</td>
        <td>${layout.dataHora(procedimento.criado_em)}</td>
        <td class="text-end">
          <div class="acoes-tabela">
            <button class="btn btn-sm btn-outline-primary" data-editar="${procedimento.id}"
                    title="Editar"><i class="bi bi-pencil-square"></i></button>
            <button class="btn btn-sm btn-outline-danger" data-excluir="${procedimento.id}"
                    data-nome="${layout.esc(procedimento.nome)}" title="Excluir">
              <i class="bi bi-trash"></i></button>
          </div>
        </td>
      </tr>`).join('');
  }

  function abrirFormulario(procedimento) {
    idEdicao = procedimento ? procedimento.id : null;
    tituloModal.textContent = procedimento ? 'Editar procedimento' : 'Novo procedimento';
    formulario.reset();
    formulario.nome.value = procedimento ? procedimento.nome : '';
    formulario.descricao.value = procedimento ? (procedimento.descricao || '') : '';
    formulario.preco.value = procedimento ? procedimento.preco : '';
    formulario.duracao_minutos.value = procedimento ? procedimento.duracao_minutos : 30;
    formulario.classList.remove('was-validated');
    modal.show();
  }

  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    if (!formulario.checkValidity()) {
      formulario.classList.add('was-validated');
      return;
    }
    const dados = {
      nome: formulario.nome.value.trim(),
      descricao: formulario.descricao.value.trim(),
      preco: formulario.preco.value,
      duracao_minutos: Number(formulario.duracao_minutos.value),
    };
    try {
      if (idEdicao) {
        const resposta = await api.atualizar('procedimentos', idEdicao, dados);
        layout.aviso(resposta.mensagem, 'success');
      } else {
        const resposta = await api.criar('procedimentos', dados);
        layout.aviso(resposta.mensagem, 'success');
      }
      modal.hide();
      idEdicao = null;
      carregar();
    } catch (erro) {
      layout.aviso(erro.message, 'danger');
    }
  });

  corpoTabela.addEventListener('click', async (evento) => {
    const botaoEditar = evento.target.closest('[data-editar]');
    const botaoExcluir = evento.target.closest('[data-excluir]');

    if (botaoEditar) {
      try {
        const resposta = await api.buscar('procedimentos', botaoEditar.dataset.editar);
        abrirFormulario(resposta.dados);
      } catch (erro) {
        layout.aviso(erro.message, 'danger');
      }
    }

    if (botaoExcluir) {
      const id = botaoExcluir.dataset.excluir;
      const nome = botaoExcluir.dataset.nome;
      const confirmado = await layout.confirmar(
        'Excluir procedimento',
        `Deseja realmente excluir o procedimento "${nome}"? ` +
        'A exclusao nao pode ser desfeita.'
      );
      if (!confirmado) return;
      try {
        const resposta = await api.excluir('procedimentos', id);
        layout.aviso(resposta.mensagem, 'success');
        carregar();
      } catch (erro) {
        layout.aviso(erro.message, 'danger');
      }
    }
  });

  document.getElementById('btn-novo').addEventListener('click', () => abrirFormulario(null));
  campoBusca.addEventListener('search', carregar);
  layout.escutarBusca(campoBusca, carregar);
  carregar();
});
