/* ==================================================================
   CRUD de Pacientes
   Endpoints: GET|POST /api/pacientes , GET|PUT|DELETE /api/pacientes/<id>
   Busca: GET /api/pacientes?busca=
   ================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  if (!layout.inicializar('pacientes', 'Pacientes',
    'Cadastro, consulta, edicao e exclusao de pacientes')) return;

  const corpoTabela = document.getElementById('corpo-tabela');
  const campoBusca = document.getElementById('campo-busca');
  const formulario = document.getElementById('formulario-paciente');
  const modal = bootstrap.Modal.getOrCreateInstance(
    document.getElementById('modal-paciente'));
  const tituloModal = document.getElementById('titulo-modal');
  let idEdicao = null;

  async function carregar() {
    try {
      const termo = campoBusca.value.trim();
      const parametros = termo ? `?busca=${encodeURIComponent(termo)}` : '';
      const resposta = await api.listar('pacientes', parametros);
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
        Nenhum paciente encontrado com o filtro informado.</div></td></tr>`;
      return;
    }
    corpoTabela.innerHTML = dados.map((paciente) => `
      <tr>
        <td>
          <strong>${layout.esc(paciente.nome)}</strong>
          <div class="text-secondary small">${layout.esc(paciente.email || '')}</div>
        </td>
        <td class="text-nowrap">${layout.esc(paciente.cpf)}</td>
        <td>${layout.data(paciente.data_nascimento)}</td>
        <td>${layout.esc(paciente.telefone || '-')}</td>
        <td>${layout.esc(paciente.endereco || '-')}</td>
        <td class="text-end">
          <div class="acoes-tabela">
            <button class="btn btn-sm btn-outline-primary" data-editar="${paciente.id}"
                    title="Editar"><i class="bi bi-pencil-square"></i></button>
            <button class="btn btn-sm btn-outline-danger" data-excluir="${paciente.id}"
                    data-nome="${layout.esc(paciente.nome)}" title="Excluir">
              <i class="bi bi-trash"></i></button>
          </div>
        </td>
      </tr>`).join('');
  }

  function abrirFormulario(paciente) {
    idEdicao = paciente ? paciente.id : null;
    tituloModal.textContent = paciente ? 'Editar paciente' : 'Novo paciente';
    formulario.reset();
    formulario.nome.value = paciente ? paciente.nome : '';
    formulario.cpf.value = paciente ? paciente.cpf : '';
    formulario.data_nascimento.value = paciente ? paciente.data_nascimento : '';
    formulario.telefone.value = paciente ? (paciente.telefone || '') : '';
    formulario.email.value = paciente ? (paciente.email || '') : '';
    formulario.endereco.value = paciente ? (paciente.endereco || '') : '';
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
      cpf: formulario.cpf.value.trim(),
      data_nascimento: formulario.data_nascimento.value,
      telefone: formulario.telefone.value.trim(),
      email: formulario.email.value.trim(),
      endereco: formulario.endereco.value.trim(),
    };
    try {
      if (idEdicao) {
        const resposta = await api.atualizar('pacientes', idEdicao, dados);
        layout.aviso(resposta.mensagem, 'success');
      } else {
        const resposta = await api.criar('pacientes', dados);
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
        const resposta = await api.buscar('pacientes', botaoEditar.dataset.editar);
        abrirFormulario(resposta.dados);
      } catch (erro) {
        layout.aviso(erro.message, 'danger');
      }
    }

    if (botaoExcluir) {
      const id = botaoExcluir.dataset.excluir;
      const nome = botaoExcluir.dataset.nome;
      const confirmado = await layout.confirmar(
        'Excluir paciente',
        `Deseja realmente excluir o paciente "${nome}"? ` +
        'A exclusao nao pode ser desfeita.'
      );
      if (!confirmado) return;
      try {
        const resposta = await api.excluir('pacientes', id);
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
