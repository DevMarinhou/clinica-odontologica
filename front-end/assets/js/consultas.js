/* ==================================================================
   CRUD de Consultas (a tela que usa o JOIN do back-end)
   Endpoints: GET|POST /api/consultas ,
              GET|PUT|DELETE /api/consultas/<id>
   Filtros : GET /api/consultas?busca=&status=&data=&paciente_id=&dentista_id=
   As opcoes dos <select> vem de:
              GET /api/pacientes , GET /api/dentistas , GET /api/procedimentos
   ================================================================== */

document.addEventListener('DOMContentLoaded', async () => {
  if (!layout.inicializar('consultas', 'Consultas',
    'Agendamentos com paciente, dentista e procedimento')) return;

  const corpoTabela = document.getElementById('corpo-tabela');
  const formulario = document.getElementById('formulario-consulta');
  const modal = bootstrap.Modal.getOrCreateInstance(
    document.getElementById('modal-consulta'));
  const tituloModal = document.getElementById('titulo-modal');
  const filtroBusca = document.getElementById('filtro-busca');
  const filtroStatus = document.getElementById('filtro-status');
  const filtroData = document.getElementById('filtro-data');
  let idEdicao = null;

  /* carrega as listas que preenchem os <select> do formulario */
  async function carregarOpcoes() {
    try {
      const [pacientes, dentistas, procedimentos] = await Promise.all([
        api.listar('pacientes'),
        api.listar('dentistas'),
        api.listar('procedimentos'),
      ]);

      formulario.paciente_id.innerHTML = '<option value="">Selecione o paciente</option>'
        + pacientes.dados.map((p) =>
          `<option value="${p.id}">${layout.esc(p.nome)} - ${layout.esc(p.cpf)}</option>`
        ).join('');

      formulario.dentista_id.innerHTML = '<option value="">Selecione o dentista</option>'
        + dentistas.dados.map((d) =>
          `<option value="${d.id}">${layout.esc(d.nome)} - ${layout.esc(d.cro)}</option>`
        ).join('');

      formulario.procedimento_id.innerHTML = '<option value="">Selecione o procedimento</option>'
        + procedimentos.dados.map((proc) =>
          `<option value="${proc.id}">${layout.esc(proc.nome)} - ${layout.moeda(proc.preco)}</option>`
        ).join('');
    } catch (erro) {
      layout.aviso(erro.message, 'danger');
    }
  }

  async function carregar() {
    try {
      const parametros = [];
      const termo = filtroBusca.value.trim();
      if (termo) parametros.push(`busca=${encodeURIComponent(termo)}`);
      if (filtroStatus.value) parametros.push(`status=${encodeURIComponent(filtroStatus.value)}`);
      if (filtroData.value) parametros.push(`data=${encodeURIComponent(filtroData.value)}`);

      const consulta = parametros.length ? `?${parametros.join('&')}` : '';
      const resposta = await api.listar('consultas', consulta);
      renderizar(resposta.dados, resposta.total);
    } catch (erro) {
      layout.aviso(erro.message, 'danger');
    }
  }

  function renderizar(dados, total) {
    document.getElementById('total-registros').textContent = total;
    if (!dados || !dados.length) {
      corpoTabela.innerHTML = `<tr><td colspan="6">
        <div class="empty-state"><i class="bi bi-calendar-x"></i>
        Nenhuma consulta encontrada com os filtros informados.</div></td></tr>`;
      return;
    }
    corpoTabela.innerHTML = dados.map((consulta) => `
      <tr>
        <td class="text-nowrap">${layout.dataHora(consulta.data_hora)}</td>
        <td>
          <strong>${layout.esc(consulta.paciente_nome)}</strong>
          <div class="text-secondary small text-nowrap">${layout.esc(consulta.paciente_cpf || '')}</div>
        </td>
        <td>
          ${layout.esc(consulta.dentista_nome)}
          <div class="text-secondary small">${layout.esc(consulta.dentista_cro || '')}</div>
        </td>
        <td>
          ${layout.esc(consulta.procedimento_nome)}
          <div class="text-secondary small">${layout.moeda(consulta.procedimento_preco)}</div>
        </td>
        <td>
          <span class="badge ${layout.classeStatus(consulta.status)} badge-status">
            ${layout.esc(consulta.status)}</span>
          <div class="text-secondary small">${layout.esc(consulta.observacoes || '')}</div>
        </td>
        <td class="text-end">
          <div class="acoes-tabela">
            <button class="btn btn-sm btn-outline-primary" data-editar="${consulta.id}"
                    title="Editar"><i class="bi bi-pencil-square"></i></button>
            <button class="btn btn-sm btn-outline-danger" data-excluir="${consulta.id}"
                    title="Excluir"><i class="bi bi-trash"></i></button>
          </div>
        </td>
      </tr>`).join('');
  }

  function abrirFormulario(consulta) {
    idEdicao = consulta ? consulta.id : null;
    tituloModal.textContent = consulta ? 'Editar consulta' : 'Nova consulta';
    formulario.reset();
    formulario.classList.remove('was-validated');

    if (consulta) {
      formulario.paciente_id.value = consulta.paciente_id;
      formulario.dentista_id.value = consulta.dentista_id;
      formulario.procedimento_id.value = consulta.procedimento_id;
      formulario.data_hora.value = layout.dataHoraParaInput(consulta.data_hora);
      formulario.status.value = consulta.status;
      formulario.observacoes.value = consulta.observacoes || '';
    } else {
      formulario.status.value = 'agendada';
      const agora = new Date(Date.now() + 3600000);
      agora.setMinutes(0, 0, 0);
      formulario.data_hora.value = layout.dataHoraParaInput(
        agora.toISOString().slice(0, 16));
    }
    modal.show();
  }

  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    if (!formulario.checkValidity()) {
      formulario.classList.add('was-validated');
      return;
    }
    const dados = {
      paciente_id: Number(formulario.paciente_id.value),
      dentista_id: Number(formulario.dentista_id.value),
      procedimento_id: Number(formulario.procedimento_id.value),
      data_hora: layout.dataHoraParaApi(formulario.data_hora.value),
      status: formulario.status.value,
      observacoes: formulario.observacoes.value.trim(),
    };
    try {
      if (idEdicao) {
        const resposta = await api.atualizar('consultas', idEdicao, dados);
        layout.aviso(resposta.mensagem, 'success');
      } else {
        const resposta = await api.criar('consultas', dados);
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
        const resposta = await api.buscar('consultas', botaoEditar.dataset.editar);
        abrirFormulario(resposta.dados);
      } catch (erro) {
        layout.aviso(erro.message, 'danger');
      }
    }

    if (botaoExcluir) {
      const id = botaoExcluir.dataset.excluir;
      const confirmado = await layout.confirmar(
        'Excluir consulta',
        'Deseja realmente excluir esta consulta? A exclusao nao pode ser desfeita.'
      );
      if (!confirmado) return;
      try {
        const resposta = await api.excluir('consultas', id);
        layout.aviso(resposta.mensagem, 'success');
        carregar();
      } catch (erro) {
        layout.aviso(erro.message, 'danger');
      }
    }
  });

  document.getElementById('btn-novo').addEventListener('click', () => abrirFormulario(null));
  filtroStatus.addEventListener('change', carregar);
  filtroData.addEventListener('change', carregar);
  layout.escutarBusca(filtroBusca, carregar);

  await carregarOpcoes();
  carregar();
});
