document.addEventListener('DOMContentLoaded', () => {

  const cpfInput = document.getElementById('cpf');

  if (cpfInput) {
    cpfInput.setAttribute('maxlength', '14');
    cpfInput.setAttribute('placeholder', '000.000.000-00');

    cpfInput.addEventListener('input', (e) => {
      let val = e.target.value;

      val = val.replace(/\D/g, '');

      val = val.slice(0, 11);


      if (val.length > 9) {
        val = val.replace(/^(\d{3})(\d{3})(\d{3})(\d{1,2})$/, '$1.$2.$3-$4');
      } else if (val.length > 6) {
        val = val.replace(/^(\d{3})(\d{3})(\d{1,3})$/, '$1.$2.$3');
      } else if (val.length > 3) {
        val = val.replace(/^(\d{3})(\d{1,3})$/, '$1.$2');
      }

      e.target.value = val;
    });


    cpfInput.addEventListener('keypress', (e) => {
      if (!/\d/.test(e.key) && e.key !== 'Backspace' && e.key !== 'Delete') {
        e.preventDefault();
      }
    });
  }

//calendario semanal
  const weekGrid      = document.getElementById('week-grid');
  const selectedTitle = document.getElementById('selected-day-title');
  const hiddenDate    = document.getElementById('hidden-date');

  const DIAS_SEMANA = ['Domingo','Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado'];
  const DIAS_CURTOS = ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'];
  const MESES      = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
                       'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];

  /**
   * retorna a data da segunda-feira da semana que contém `d`.
   * @param {Date} d
   * @returns {Date}
   */
  function getMonday(d) {
    const date  = new Date(d);
    const day   = date.getDay(); 
    const diff  = (day === 0) ? -6 : 1 - day; 
    date.setDate(date.getDate() + diff);
    date.setHours(0, 0, 0, 0);
    return date;
  }

  /**
   * formata um date para "YYYY-MM-DD"
   * @param {Date} d
   * @returns {string}
   */
  function toISO(d) {
    const yyyy = d.getFullYear();
    const mm   = String(d.getMonth() + 1).padStart(2, '0');
    const dd   = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  /**
   * formata um date para texto corrido em português.
   * @param {Date} d
   * @returns {string}
   */
  function toLongDate(d) {
    return `${DIAS_SEMANA[d.getDay()]}, ${d.getDate()} de ${MESES[d.getMonth()]} de ${d.getFullYear()}`;
  }

  if (weekGrid) {
    const today  = new Date();
    const monday = getMonday(today);

    // cards
    for (let i = 0; i < 5; i++) {
      const dayDate = new Date(monday);
      dayDate.setDate(monday.getDate() + i);

      const isToday = toISO(dayDate) === toISO(today);

      const card = document.createElement('div');
      card.className = 'day-card' + (isToday ? ' active' : '');
      card.dataset.date = toISO(dayDate);
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');
      card.setAttribute('aria-label', toLongDate(dayDate));

      card.innerHTML = `
        <div class="day-name">${DIAS_CURTOS[dayDate.getDay()]}</div>
        <div class="day-number">${dayDate.getDate()}</div>
        <div class="day-month">${MESES[dayDate.getMonth()].slice(0, 3)}</div>
      `;

      const selectDay = () => {
        weekGrid.querySelectorAll('.day-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');


        if (selectedTitle) {
          selectedTitle.textContent = toLongDate(dayDate);
        }

        if (hiddenDate) {
          hiddenDate.value = toISO(dayDate);
        }
      };

      card.addEventListener('click', selectDay);
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          selectDay();
        }
      });

      weekGrid.appendChild(card);

      if (isToday) {
        if (selectedTitle) selectedTitle.textContent = toLongDate(today);
        if (hiddenDate)    hiddenDate.value           = toISO(today);
      }
    }

    const todayDay = today.getDay();
    if (todayDay === 0 || todayDay === 6) {
      const firstCard = weekGrid.querySelector('.day-card');
      if (firstCard) {
        firstCard.classList.add('active');
        if (selectedTitle) selectedTitle.textContent = toLongDate(monday);
        if (hiddenDate)    hiddenDate.value           = toISO(monday);
      }
    }
  }


  const modalOverlay   = document.getElementById('modal-agendamento');
  const modalHorario   = document.getElementById('modal-horario');   
  const modalInputHora = document.getElementById('modal-input-hora'); 
  const modalInputData = document.getElementById('modal-input-data'); 

  /**
   * Abre o modal preenchendo as informações do horário clicado.
   * Chamada pelo atributo onclick dos cards de horário no HTML.
   * @param {string} horario - Ex.: "10:00"
   */
  window.abrirModal = function(horario) {
    if (!modalOverlay) return;


    const dataAtual = hiddenDate ? hiddenDate.value : toISO(new Date());


    let textoData = dataAtual;
    if (dataAtual) {

      const [y, m, d] = dataAtual.split('-').map(Number);
      const dt = new Date(y, m - 1, d);
      textoData = toLongDate(dt);
    }

    if (modalHorario) {
      modalHorario.textContent = `${horario} — ${textoData}`;
    }
    if (modalInputHora) modalInputHora.value = horario + ':00'; 
    if (modalInputData) modalInputData.value = dataAtual;


    const campoDataHora = document.getElementById('modal-input-data-hora');
    if (campoDataHora && dataAtual) {
      campoDataHora.value = `${dataAtual} ${horario}:00`;
    }

    modalOverlay.classList.add('open');
    document.body.style.overflow = 'hidden';


    setTimeout(() => {
      const primeiro = modalOverlay.querySelector('select, input:not([type="hidden"]), button');
      if (primeiro) primeiro.focus();
    }, 80);
  };

  /**
   * Fecha o modal de agendamento.
   * Chamada pelo botão "Cancelar" ou pelo clique no overlay.
   */
  window.fecharModal = function() {
    if (!modalOverlay) return;
    modalOverlay.classList.remove('open');
    document.body.style.overflow = '';
  };


  if (modalOverlay) {
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) window.fecharModal();
    });


    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modalOverlay.classList.contains('open')) {
        window.fecharModal();
      }
    });
  }


  document.querySelectorAll('[data-edit-field]').forEach(btn => {
    btn.addEventListener('click', () => {
      const fieldName  = btn.dataset.editField;
      const fieldValue = document.getElementById(`value-${fieldName}`);
      const fieldInput = document.getElementById(`input-${fieldName}`);
      const saveBtn    = document.getElementById(`save-${fieldName}`);
      const cancelBtn  = document.getElementById(`cancel-${fieldName}`);

      if (!fieldValue || !fieldInput) return;

      // modo edição
      fieldInput.value = fieldValue.textContent.trim();
      fieldValue.style.display = 'none';
      fieldInput.style.display = 'block';
      if (saveBtn)   saveBtn.style.display   = 'inline-flex';
      if (cancelBtn) cancelBtn.style.display = 'inline-flex';
      btn.style.display = 'none';
      fieldInput.focus();
    });
  });

  document.querySelectorAll('[data-cancel-field]').forEach(btn => {
    btn.addEventListener('click', () => {
      const fieldName  = btn.dataset.cancelField;
      resetField(fieldName);
    });
  });

  function resetField(fieldName) {
    const fieldValue = document.getElementById(`value-${fieldName}`);
    const fieldInput = document.getElementById(`input-${fieldName}`);
    const saveBtn    = document.getElementById(`save-${fieldName}`);
    const cancelBtn  = document.getElementById(`cancel-${fieldName}`);
    const editBtn    = document.querySelector(`[data-edit-field="${fieldName}"]`);

    if (fieldValue) fieldValue.style.display = '';
    if (fieldInput) fieldInput.style.display  = 'none';
    if (saveBtn)    saveBtn.style.display     = 'none';
    if (cancelBtn)  cancelBtn.style.display   = 'none';
    if (editBtn)    editBtn.style.display     = '';
  }


  const senhaInput     = document.getElementById('senha');
  const confirmarInput = document.getElementById('confirmar_senha');
  const senhaFeedback  = document.getElementById('senha-feedback');

  if (senhaInput && confirmarInput) {
    const checkSenhas = () => {
      if (!confirmarInput.value) return;
      const match = senhaInput.value === confirmarInput.value;
      confirmarInput.style.borderColor = match ? 'var(--success)' : 'var(--danger)';
      if (senhaFeedback) {
        senhaFeedback.textContent = match ? '✓ Senhas coincidem' : '✗ Senhas não conferem';
        senhaFeedback.style.color = match ? 'var(--success)' : 'var(--danger)';
      }
    };
    confirmarInput.addEventListener('input', checkSenhas);
    senhaInput.addEventListener('input', checkSenhas);
  }

  document.querySelectorAll('.message-item').forEach(msg => {
    msg.style.cursor = 'pointer';
    msg.title = 'Clique para fechar';
    msg.addEventListener('click', () => {
      msg.style.opacity = '0';
      msg.style.transition = 'opacity 0.3s';
      setTimeout(() => msg.remove(), 320);
    });
  });

}); 
