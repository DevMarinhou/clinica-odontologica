/* ==================================================================
   CRUD de Usuarios (usuario e senha do sistema)
   Endpoints: GET|POST /api/usuarios ,
              GET|PUT|DELETE /api/usuarios/<id>
   Busca: GET /api/usuarios?busca=
   Observacao: a senha NUNCA volta da API - no cadastro e na edicao
   ela e enviada apenas para gravar o hash.
   ================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  if (!layout.inicializar('usuarios', 'Usuarios',
    'Acesso ao sistema: usuario, senha e perfil')) return;

  const corpoTabela = document.getElementById('corpo-tabela');
  const campoBusca = document.getElementById('campo-busca');
  const formulario = document.getElementById('formulario-usuario');
  const modal = bootstrap.Modal.getOrCreateInstance(
    document.getElementById('modal-usuario'));
  const tituloModal = document.getElementById('titulo-modal');
  const rotuloSenha = document.getElementById('rotulo-senha');
  const ajudaSenha = document.getElementById('ajuda-senha');
  let idEdicao = null;

  async function carregar() {
    try {
      const termo = campoBusca.value.trim();
      const parametros = termo ? `?busca=${encodeURIComponent(termo)}` : '';
      const resposta = await api.listar('usuarios', parametros);
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
        Nenhum usuario encontrado com o filtro informado.</div></td></tr>`;
      return;
    }
    corpoTabela.innerHTML = dados.map((usuario) => `
      <tr>
        <td><strong>${layout.esc(usuario.nome_usuario)}</strong></td>
        <td>${layout.esc(usuario.nome_completo)}</td>
        <td><span class="badge text-bg-light border">${layout.esc(usuario.perfil)}</span></td>
        <td>
          ${usuario.ativo
            ? '<span class="badge text-bg-success badge-status">Ativo</span>'
            : '<span class="badge text-bg-secondary badge-status">Inativo</span>'}
        </td>
        <td>${layout.dataHora(usuario.criado_em)}</td>
        <td class="text-end">
          <div class="acoes-tabela">
            <button class="btn btn-sm btn-outline-primary" data-editar="${usuario.id}"
                    title="Editar"><i class="bi bi-pencil-square"></i></button>
            <button class="btn btn-sm btn-outline-danger" data-excluir="${usuario.id}"
                    data-nome="${layout.esc(usuario.nome_usuario)}" title="Excluir">
              <i class="bi bi-trash"></i></button>
          </div>
        </td>
      </tr>`).join('');
  }

  function abrirFormulario(usuario) {
    idEdicao = usuario ? usuario.id : null;
    tituloModal.textContent = usuario ? 'Editar usuario' : 'Novo usuario';
    formulario.reset();
    formulario.nome_usuario.value = usuario ? usuario.nome_usuario : '';
    formulario.nome_completo.value = usuario ? usuario.nome_completo : '';
    formulario.perfil.value = usuario ? usuario.perfil : 'recepcao';
    formulario.ativo.checked = usuario ? !!usuario.ativo : true;
    formulario.senha.value = '';

    if (usuario) {
      // na edicao a senha e opcional: so troque se digitar uma nova
      formulario.senha.required = false;
      rotuloSenha.textContent = 'Nova senha (opcional)';
      ajudaSenha.textContent = 'Deixe em branco para manter a senha atual.';
    } else {
      formulario.senha.required = true;
      rotuloSenha.textContent = 'Senha';
      ajudaSenha.textContent = 'Minimo de 6 caracteres.';
    }
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
      nome_usuario: formulario.nome_usuario.value.trim(),
      nome_completo: formulario.nome_completo.value.trim(),
      perfil: formulario.perfil.value,
      ativo: formulario.ativo.checked ? 1 : 0,
    };
    if (formulario.senha.value.trim()) {
      dados.senha = formulario.senha.value;
    }

    try {
      if (idEdicao) {
        const resposta = await api.atualizar('usuarios', idEdicao, dados);
        layout.aviso(resposta.mensagem, 'success');
      } else {
        const resposta = await api.criar('usuarios', dados);
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
        const resposta = await api.buscar('usuarios', botaoEditar.dataset.editar);
        abrirFormulario(resposta.dados);
      } catch (erro) {
        layout.aviso(erro.message, 'danger');
      }
    }

    if (botaoExcluir) {
      const id = botaoExcluir.dataset.excluir;
      const nome = botaoExcluir.dataset.nome;
      const confirmado = await layout.confirmar(
        'Excluir usuario',
        `Deseja realmente excluir o usuario "${nome}"? ` +
        'A exclusao nao pode ser desfeita.'
      );
      if (!confirmado) return;
      try {
        const resposta = await api.excluir('usuarios', id);
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
