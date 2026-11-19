/* ==================================================================
   Tela inicial: login + painel principal
   Endpoints: POST /api/auth/login  e  GET /api/painel/resumo
   ================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  const telaLogin = document.getElementById('tela-login');
  const telaPainel = document.getElementById('tela-painel');
  const formularioLogin = document.getElementById('formulario-login');
  const alertaLogin = document.getElementById('alerta-login');

  function mostrarPainel() {
    telaLogin.classList.add('d-none');
    telaPainel.classList.remove('d-none');
    layout.montarMenu('painel');
    layout.montarTopo('Painel', 'Resumo dos indicadores da clinica');
    carregarPainel();
  }

  async function carregarPainel() {
    try {
      const resposta = await api.painel();
      const dados = resposta.dados;
      const totais = dados.totais || {};

      document.getElementById('total-pacientes').textContent = totais.pacientes ?? 0;
      document.getElementById('total-dentistas').textContent = totais.dentistas ?? 0;
      document.getElementById('total-procedimentos').textContent = totais.procedimentos ?? 0;
      document.getElementById('total-consultas').textContent = totais.consultas ?? 0;
      document.getElementById('total-usuarios').textContent = totais.usuarios ?? 0;
      document.getElementById('consultas-hoje').textContent = dados.consultas_hoje ?? 0;
      document.getElementById('consultas-pendentes').textContent = dados.consultas_pendentes ?? 0;
      document.getElementById('faturamento').textContent = layout.moeda(dados.faturamento_concluido);

      // consultas por status
      const listaStatus = document.getElementById('lista-status');
      const status = dados.consultas_por_status || [];
      listaStatus.innerHTML = status.length
        ? status.map((item) => `
          <li class="d-flex justify-content-between align-items-center py-2 border-bottom">
            <span><span class="badge ${layout.classeStatus(item.status)} badge-status">${layout.esc(item.status)}</span></span>
            <strong>${item.quantidade}</strong>
          </li>`).join('')
        : '<li class="text-secondary py-2">Nenhuma consulta registrada.</li>';

      // proximas consultas
      const corpo = document.getElementById('corpo-proximas');
      const proximas = dados.proximas_consultas || [];
      corpo.innerHTML = proximas.length
        ? proximas.map((consulta) => `
          <tr>
            <td>${layout.dataHora(consulta.data_hora)}</td>
            <td>${layout.esc(consulta.paciente_nome)}</td>
            <td>${layout.esc(consulta.dentista_nome)}</td>
            <td>${layout.esc(consulta.procedimento_nome)}</td>
            <td><span class="badge ${layout.classeStatus(consulta.status)} badge-status">${layout.esc(consulta.status)}</span></td>
          </tr>`).join('')
        : `<tr><td colspan="5"><div class="empty-state">
             <i class="bi bi-calendar-x"></i>Nenhuma consulta agendada para as proximas datas.
           </div></td></tr>`;
    } catch (erro) {
      layout.aviso(erro.message, 'danger');
    }
  }

  formularioLogin.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    alertaLogin.classList.add('d-none');

    const nome_usuario = formularioLogin.nome_usuario.value.trim();
    const senha = formularioLogin.senha.value;
    if (!nome_usuario || !senha) {
      alertaLogin.textContent = 'Informe o usuario e a senha.';
      alertaLogin.classList.remove('d-none');
      return;
    }

    const botao = formularioLogin.querySelector('button[type="submit"]');
    botao.disabled = true;
    botao.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Entrando...';

    try {
      const resposta = await api.login(nome_usuario, senha);
      layout.guardarUsuario(resposta.dados);
      formularioLogin.reset();
      mostrarPainel();
    } catch (erro) {
      alertaLogin.textContent = erro.message;
      alertaLogin.classList.remove('d-none');
    } finally {
      botao.disabled = false;
      botao.innerHTML = 'Entrar';
    }
  });

  // ja logado? vai direto para o painel
  if (layout.usuarioAtual()) {
    mostrarPainel();
  }
});
