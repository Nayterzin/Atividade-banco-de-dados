document.addEventListener('DOMContentLoaded', () => {


  const cpfInput = document.getElementById('cpf') || document.getElementById('usuario');

  if (cpfInput) {
    cpfInput.setAttribute('maxlength', '14');

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
  }

 
  const editButtons = document.querySelectorAll('[data-edit-field]');

  editButtons.forEach(button => {
    button.addEventListener('click', (e) => {
      const fieldName = e.target.getAttribute('data-edit-field');
      
      
      const valueSpan = document.getElementById(`value-${fieldName}`);
      const inputField = document.getElementById(`input-${fieldName}`);
      const saveButton = document.getElementById(`save-${fieldName}`);
      const formInline = document.getElementById(`form-${fieldName}`);

      
      if (formInline) {
        valueSpan.style.display = 'none';
        e.target.style.display = 'none';
        formInline.style.display = 'flex';
        inputField.style.display = 'inline-block';
        inputField.focus();
      } else {
        
        if (valueSpan)  valueSpan.style.display  = 'none';
        if (inputField) {
          inputField.style.display = 'inline-block';
          inputField.focus();
        }
        if (saveButton) saveButton.style.display = 'inline-block';
        e.target.style.display = 'none';
      }
    });
  });

 
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