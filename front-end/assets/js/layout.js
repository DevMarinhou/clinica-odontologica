/* ==================================================================
   Layout comum: menu lateral, topo, login, avisos e formatacao.
   ================================================================== */

const layout = (() => {
  const CHAVE_SESSAO = 'clinica_usuario';

  const PAGINAS = [
    { id: 'painel', rotulo: 'Painel', icone: 'bi-speedometer2', href: 'index.html' },
    { id: 'pacientes', rotulo: 'Pacientes', icone: 'bi-people', href: 'pacientes.html' },
    { id: 'dentistas', rotulo: 'Dentistas', icone: 'bi-person-badge', href: 'dentistas.html' },
    { id: 'procedimentos', rotulo: 'Procedimentos', icone: 'bi-clipboard2-pulse', href: 'procedimentos.html' },
    { id: 'consultas', rotulo: 'Consultas', icone: 'bi-calendar-week', href: 'consultas.html' },
    { id: 'usuarios', rotulo: 'Usuarios', icone: 'bi-shield-lock', href: 'usuarios.html' },
  ];

  /* ---------------- sessao ---------------- */
  function usuarioAtual() {
    try {
      return JSON.parse(localStorage.getItem(CHAVE_SESSAO));
    } catch (erro) {
      return null;
    }
  }

  function guardarUsuario(usuario) {
    localStorage.setItem(CHAVE_SESSAO, JSON.stringify(usuario));
  }

  function sair() {
    localStorage.removeItem(CHAVE_SESSAO);
    window.location.href = 'index.html';
  }

  function exigirLogin() {
    if (!usuarioAtual()) {
      window.location.href = 'index.html';
      return false;
    }
    return true;
  }

  /* ---------------- estrutura da pagina ---------------- */
  function montarMenu(paginaAtual) {
    const usuario = usuarioAtual() || {};
    const itens = PAGINAS.map((pagina) => `
      <li>
        <a href="${pagina.href}" class="${pagina.id === paginaAtual ? 'ativo' : ''}">
          <i class="bi ${pagina.icone}"></i> ${pagina.rotulo}
        </a>
      </li>`).join('');

    document.getElementById('sidebar').innerHTML = `
      <div class="marca">
        <i class="bi bi-heart-pulse"></i>
        <div>
          <strong>Clinica Odontologica</strong>
          <small>Sistema de Gestao</small>
        </div>
      </div>
      <ul class="menu-lateral">
        <li class="titulo-secao">Menu</li>
        ${itens}
      </ul>
      <div class="rodape-menu">
        <div class="d-flex align-items-center gap-2">
          <i class="bi bi-person-circle"></i>
          <span>${usuario.nome_completo || 'Usuario'}</span>
        </div>
        <div class="text-secondary mt-1" style="font-size:.75rem;">
          Perfil: ${usuario.perfil || '-'}
        </div>
      </div>`;
  }

  function montarTopo(titulo, subtitulo) {
    const usuario = usuarioAtual() || {};
    document.getElementById('titulo-pagina').innerHTML =
      `${titulo} <small>${subtitulo || ''}</small>`;
    document.getElementById('usuario-logado').textContent =
      usuario.nome_completo || usuario.nome_usuario || '';
    document.getElementById('btn-sair').addEventListener('click', sair);
  }

  /* Inicializa as paginas do sistema (exceto a tela de login) */
  function inicializar(paginaAtual, titulo, subtitulo) {
    if (!exigirLogin()) return false;
    montarMenu(paginaAtual);
    montarTopo(titulo, subtitulo);

    const botao = document.getElementById('btn-menu');
    if (botao) {
      botao.addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('aberta');
      });
    }
    return true;
  }

  /* ---------------- avisos (toast) ---------------- */
  function aviso(mensagem, tipo = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container position-fixed top-0 end-0 p-3';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${tipo} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">${mensagem}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto"
                data-bs-dismiss="toast"></button>
      </div>`;
    container.appendChild(toast);
    const instancia = new bootstrap.Toast(toast, { delay: 3500 });
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
    instancia.show();
  }

  /* ---------------- confirmacao de exclusao ---------------- */
  function confirmar(titulo, mensagem, textoBotao = 'Excluir') {
    return new Promise((resolve) => {
      let modal = document.getElementById('modal-confirmacao');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal-confirmacao';
        modal.className = 'modal fade';
        modal.innerHTML = `
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title"></h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body"></div>
              <div class="modal-footer">
                <button type="button" class="btn btn-outline-secondary"
                        data-bs-dismiss="modal">Cancelar</button>
                <button type="button" class="btn btn-danger" id="btn-confirmar-acao"></button>
              </div>
            </div>
          </div>`;
        document.body.appendChild(modal);
      }
      modal.querySelector('.modal-title').textContent = titulo;
      modal.querySelector('.modal-body').textContent = mensagem;
      modal.querySelector('#btn-confirmar-acao').textContent = textoBotao;

      const instancia = bootstrap.Modal.getOrCreateInstance(modal);
      const botao = modal.querySelector('#btn-confirmar-acao');

      const aoConfirmar = () => {
        instancia.hide();
        resolve(true);
      };
      botao.replaceWith(botao.cloneNode(true));
      modal.querySelector('#btn-confirmar-acao')
        .addEventListener('click', aoConfirmar, { once: true });
      modal.addEventListener('hidden.bs.modal', () => resolve(false), { once: true });
      instancia.show();
    });
  }

  /* ---------------- formatacao ---------------- */
  function esc(texto) {
    if (texto === null || texto === undefined) return '';
    const codigos = {
      '&': 38, '<': 60, '>': 62, '"': 34, "'": 39,
    };
    return String(texto).replace(
      /[&<>"']/g,
      (caractere) => String.fromCharCode(codigos[caractere])
    );
  }

  function data(valor) {
    if (!valor) return '-';
    const partes = String(valor).slice(0, 10).split('-');
    if (partes.length !== 3) return valor;
    return `${partes[2]}/${partes[1]}/${partes[0]}`;
  }

  function dataHora(valor) {
    if (!valor) return '-';
    const d = new Date(valor);
    if (isNaN(d.getTime())) return valor;
    return d.toLocaleString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  function moeda(valor) {
    return Number(valor || 0).toLocaleString('pt-BR', {
      style: 'currency', currency: 'BRL',
    });
  }

  /* valor do <input type="datetime-local"> -> formato da API */
  function dataHoraParaApi(valor) {
    if (!valor) return '';
    return valor.replace('T', ' ');
  }

  /* valor da API ("2026-11-19T15:30:00") -> <input datetime-local> */
  function dataHoraParaInput(valor) {
    if (!valor) return '';
    return String(valor).slice(0, 16);
  }

  function classeStatus(status) {
    const mapa = {
      agendada: 'text-bg-secondary',
      confirmada: 'text-bg-primary',
      em_andamento: 'text-bg-warning',
      concluida: 'text-bg-success',
      cancelada: 'text-bg-danger',
    };
    return mapa[status] || 'text-bg-secondary';
  }

  function escutarBusca(campo, aoBuscar, atraso = 350) {
    let temporizador;
    campo.addEventListener('input', () => {
      clearTimeout(temporizador);
      temporizador = setTimeout(aoBuscar, atraso);
    });
  }

  return {
    inicializar, montarMenu, montarTopo, aviso, confirmar, data, dataHora, moeda,
    dataHoraParaApi, dataHoraParaInput, classeStatus, escutarBusca, esc,
    usuarioAtual, guardarUsuario, sair, exigirLogin,
  };
})();
