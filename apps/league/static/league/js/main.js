// Junior Baseball League - interacciones ligeras del lado del cliente
document.addEventListener('DOMContentLoaded', () => {
    // Confirmación antes de enviar cualquier formulario de eliminación
    document.querySelectorAll('form[data-confirm]').forEach((form) => {
        form.addEventListener('submit', (event) => {
            const message = form.getAttribute('data-confirm') || '¿Estás seguro?';
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Auto-cierre de las alertas de mensajes después de unos segundos
    document.querySelectorAll('.alert[data-auto-dismiss]').forEach((alert) => {
        setTimeout(() => {
            alert.classList.remove('show');
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 300);
        }, 4000);
    });
});
