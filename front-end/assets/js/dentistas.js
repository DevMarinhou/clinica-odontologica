/* ==================================================================
   CRUD de Dentistas
   Endpoints: GET|POST /api/dentistas , GET|PUT|DELETE /api/dentistas/<id>
   Busca: GET /api/dentistas?busca=
   ================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  if (!layout.inicializar('dentistas', 'Dentistas',
    'Profissionais da clinica, com registro no conselho (CRO)')) return;

  const corpoTabela = document.getElementById('corpo-tabela');
  const campoBusca = document.getElementById('campo-busca');
  const formulario = document.getElementById('formulario-dentista');
  const modal = bootstrap.Modal.getOrCreateInstance(
    document.getElementById('modal-dentista'));
  const tituloModal = document.getElementById('titulo-modal');
  let idEdicao = null;

  async function carregar() {
    try {
      const termo = campoBusca.value.trim();
      const parametros = termo ? `?busca=${encodeURIComponent(termo)}` : '';
      const resposta = await api.listar('dentistas', parametros);
      renderizar(resposta.dados, resposta.total);
    } catch (erro) {
      layout.aviso(erro.message, 'danger');
    }
  }

  function renderizar(dados, total) {
    document.getElementById('total-registros').textContent = total;
    if (!dados || !dados.length) {
      corpoTabela.innerHTML = `<tr><td colspan="6">
        <div class="empty-state"><i class="bi bi-inbox"></i>
        Nenhum dentista encontrado com o filtro informado.</div></td></tr>`;
      return;
    }
    corpoTabela.innerHTML = dados.map((dentista) => `
      <tr>
        <td>
          <strong>${layout.esc(dentista.nome)}</strong>
          <div class="text-secondary small">${layout.esc(dentista.email || '')}</div>
        </td>
        <td><span class="badge text-bg-light border">${layout.esc(dentista.cro)}</span></td>
        <td>${layout.esc(dentista.especialidade || '-')}</td>
        <td>${layout.esc(dentista.telefone || '-')}</td>
        <td>
          ${dentista.ativo
            ? '<span class="badge text-bg-success badge-status">Ativo</span>'
            : '<span class="badge text-bg-secondary badge-status">Inativo</span>'}
        </td>
        <td class="text-end">
          <div class="acoes-tabela">
            <button class="btn btn-sm btn-outline-primary" data-editar="${dentista.id}"
                    title="Editar"><i class="bi bi-pencil-square"></i></button>
            <button class="btn btn-sm btn-outline-danger" data-excluir="${dentista.id}"
                    data-nome="${layout.esc(dentista.nome)}" title="Excluir">
              <i class="bi bi-trash"></i></button>
          </div>
        </td>
      </tr>`).join('');
  }

  function abrirFormulario(dentista) {
    idEdicao = dentista ? dentista.id : null;
    tituloModal.textContent = dentista ? 'Editar dentista' : 'Novo dentista';
    formulario.reset();
    formulario.nome.value = dentista ? dentista.nome : '';
    formulario.cro.value = dentista ? dentista.cro : '';
    formulario.especialidade.value = dentista ? (dentista.especialidade || '') : '';
    formulario.telefone.value = dentista ? (dentista.telefone || '') : '';
    formulario.email.value = dentista ? (dentista.email || '') : '';
    formulario.ativo.checked = dentista ? !!dentista.ativo : true;
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
      cro: formulario.cro.value.trim(),
      especialidade: formulario.especialidade.value.trim(),
      telefone: formulario.telefone.value.trim(),
      email: formulario.email.value.trim(),
      ativo: formulario.ativo.checked ? 1 : 0,
    };
    try {
      if (idEdicao) {
        const resposta = await api.atualizar('dentistas', idEdicao, dados);
        layout.aviso(resposta.mensagem, 'success');
      } else {
        const resposta = await api.criar('dentistas', dados);
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
        const resposta = await api.buscar('dentistas', botaoEditar.dataset.editar);
        abrirFormulario(resposta.dados);
      } catch (erro) {
        layout.aviso(erro.message, 'danger');
      }
    }

    if (botaoExcluir) {
      const id = botaoExcluir.dataset.excluir;
      const nome = botaoExcluir.dataset.nome;
      const confirmado = await layout.confirmar(
        'Excluir dentista',
        `Deseja realmente excluir o dentista "${nome}"? ` +
        'A exclusao nao pode ser desfeita.'
      );
      if (!confirmado) return;
      try {
        const resposta = await api.excluir('dentistas', id);
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
