const API_URL = 'http://localhost:8000';
let threadId = null;
let oportunidadParaCambiarEstado = null;
let historialImagenes = [];

document.addEventListener('DOMContentLoaded', function () {
    cargarOportunidades();
    configurarUploadImagen();
    cargarHistorialImagenes();
});

// ==================== CONSULTAS RAG ====================

function hacerPregunta() {
    const pregunta = document.getElementById('pregunta').value.trim();

    if (!pregunta) {
        mostrarAlerta('Por favor escribe una pregunta', 'warning');
        return;
    }

    const div = document.getElementById('respuestaDiv');
    div.innerHTML = '<div class="response-active"><p><span class="loading">⟳</span> Procesando tu pregunta...</p></div>';

    const payload = {
        pregunta: pregunta,
        thread_id: threadId
    };

    fetch(`${API_URL}/consultar`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            threadId = data.thread_id;
            const respuesta = data.respuesta;

            div.innerHTML = `
            <div class="response-active">
                <h3>Respuesta del sistema</h3>
                <p>${escapeHtml(respuesta)}</p>
                <div class="response-meta">
                    <strong>Thread ID:</strong> ${threadId} | 
                    <strong>Fuentes:</strong> Catálogo, Políticas, Proceso CRM
                </div>
            </div>
        `;

            document.getElementById('pregunta').value = '';

            const indicador = document.getElementById('threadIndicador');
            if (indicador) {
                indicador.textContent = `Conversación activa: ${threadId}`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            div.innerHTML = `
            <div class="response-active" style="color: #dc3545;">
                <h3>Error al procesar</h3>
                <p>${escapeHtml(error.message)}</p>
                <p style="font-size: 12px; margin-top: 8px;">Verifica que el backend esté ejecutándose en ${API_URL}</p>
            </div>
        `;
        });
}

function nuevaConversacion() {
    threadId = null;

    const div = document.getElementById('respuestaDiv');
    div.innerHTML = `
        <div class="response-empty">
            <p>Escribe una pregunta para comenzar...</p>
        </div>
    `;

    document.getElementById('pregunta').value = '';

    const indicador = document.getElementById('threadIndicador');
    if (indicador) {
        indicador.textContent = '';
    }

    mostrarAlerta('Nueva conversación iniciada', 'success');
}

// ==================== ANÁLISIS DE IMAGEN ====================

function configurarUploadImagen() {
    const fileUpload = document.getElementById('fileUpload');
    const imageInput = document.getElementById('imageInput');

    fileUpload.addEventListener('click', () => imageInput.click());

    fileUpload.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileUpload.style.background = 'rgba(0, 123, 255, 0.15)';
    });

    fileUpload.addEventListener('dragleave', () => {
        fileUpload.style.background = 'rgba(0, 123, 255, 0.05)';
    });

    fileUpload.addEventListener('drop', (e) => {
        e.preventDefault();
        fileUpload.style.background = 'rgba(0, 123, 255, 0.05)';

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            imageInput.files = files;
            mostrarPreview(files[0]);
        }
    });

    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            mostrarPreview(e.target.files[0]);
        }
    });
}

function mostrarPreview(file) {
    const reader = new FileReader();

    reader.onload = function (e) {
        const previewDiv = document.getElementById('previewImagen');
        const previewImg = document.getElementById('previewImg');
        previewImg.src = e.target.result;
        previewDiv.style.display = 'block';

        const fileUpload = document.getElementById('fileUpload');
        fileUpload.style.display = 'none';
    };

    reader.readAsDataURL(file);
}

function analizarImagen() {
    const imageInput = document.getElementById('imageInput');
    const descriptionImagen = document.getElementById('descriptionImagen').value.trim();

    if (!imageInput.files || imageInput.files.length === 0) {
        mostrarAlerta('Por favor selecciona una imagen', 'warning');
        return;
    }

    if (!descriptionImagen) {
        mostrarAlerta('Especifica qué quieres consultar de la imagen', 'warning');
        return;
    }

    const file = imageInput.files[0];
    const reader = new FileReader();

    reader.onload = function (e) {
        const base64Full = e.target.result;
        const base64 = base64Full.split(',')[1];

        const timestamp = new Date().toLocaleString();
        const nombreArchivo = `imagen_${Date.now()}.png`;

        const div = document.getElementById('imageResponseDiv');
        div.style.display = 'block';
        div.innerHTML = '<div class="response-active"><p><span class="loading">⟳</span> Analizando imagen...</p></div>';

        const payload = {
            imagen_base64: base64,
            descripcion: descriptionImagen,
            thread_id: threadId
        };

        fetch(`${API_URL}/analizar-imagen`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
            .then(response => {
                if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
                return response.json();
            })
            .then(data => {
                const resultado = data.respuesta;

                div.innerHTML = `
                <div class="response-active">
                    <h3>Resultado del análisis</h3>
                    <p>${escapeHtml(resultado)}</p>
                    <div class="response-meta">
                        <strong>Imagen:</strong> <span id="imagenNombre">${nombreArchivo}</span> | 
                        <strong>Guardada:</strong> <span id="imagenGuardada">${timestamp}</span>
                    </div>
                </div>
            `;

                // NOTA: ya no se guarda el base64 de la imagen en el historial
                // (localStorage tiene un limite de 5-10 MB por dominio, y las
                // imagenes en base64 lo llenan rapido). La imagen real ya queda
                // guardada por el backend en data/imagenes_consultadas/; aqui
                // solo se guardan metadatos livianos para el historial visual.
                const registro = {
                    id: Date.now(),
                    nombre: nombreArchivo,
                    timestamp: timestamp,
                    descripcion: descriptionImagen,
                    resultado: resultado.substring(0, 100) + '...'
                };

                historialImagenes.unshift(registro);

                const MAX_HISTORIAL = 20;
                if (historialImagenes.length > MAX_HISTORIAL) {
                    historialImagenes = historialImagenes.slice(0, MAX_HISTORIAL);
                }

                guardarHistorialEnStorage();
                cargarHistorialImagenes();

                document.getElementById('imageInput').value = '';
                document.getElementById('descriptionImagen').value = '';
                document.getElementById('previewImagen').style.display = 'none';
                document.getElementById('fileUpload').style.display = 'block';

                mostrarAlerta('Imagen analizada y guardada correctamente', 'success');
            })
            .catch(error => {
                console.error('Error:', error);
                div.innerHTML = `
                <div class="response-active" style="color: #dc3545;">
                    <h3>Error al analizar imagen</h3>
                    <p>${escapeHtml(error.message)}</p>
                </div>
            `;
                mostrarAlerta(`Error: ${error.message}`, 'error');
            });
    };

    reader.readAsDataURL(file);
}

function guardarHistorialEnStorage() {
    try {
        localStorage.setItem('historialImagenes', JSON.stringify(historialImagenes));
    } catch (error) {
        console.error('Error al guardar historial:', error);

        if (error.name === 'QuotaExceededError' || error.code === 22) {
            if (historialImagenes.length > 1) {
                historialImagenes.pop();
                try {
                    localStorage.setItem('historialImagenes', JSON.stringify(historialImagenes));
                    mostrarAlerta('Se eliminó el registro más antiguo del historial por límite de espacio', 'warning');
                } catch (error2) {
                    mostrarAlerta('No hay espacio suficiente para guardar más registros en el historial', 'error');
                }
            } else {
                mostrarAlerta('No se pudo guardar el registro en el historial', 'error');
            }
        }
    }
}

function cargarHistorialImagenes() {
    const historialGuardado = localStorage.getItem('historialImagenes');
    if (historialGuardado) {
        historialImagenes = JSON.parse(historialGuardado);
    }

    const historialDiv = document.getElementById('imageHistorialDiv');

    if (historialImagenes.length === 0) {
        historialDiv.innerHTML = '<div class="empty-state">No hay imágenes analizadas aún</div>';
        return;
    }

    const html = `
        <table>
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Nombre</th>
                    <th>Descripción</th>
                    <th>Resultado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                ${historialImagenes.map(img => `
                    <tr>
                        <td style="font-size: 12px;">${img.timestamp}</td>
                        <td><strong>${escapeHtml(img.nombre)}</strong></td>
                        <td style="max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(img.descripcion)}</td>
                        <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 12px;">${escapeHtml(img.resultado)}</td>
                        <td>
                            <button class="btn btn-sm" onclick="eliminarDelHistorial(${img.id})">Eliminar</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    historialDiv.innerHTML = html;
}

function eliminarDelHistorial(id) {
    if (!confirm('¿Estás seguro de que quieres eliminar este registro del historial?')) return;

    historialImagenes = historialImagenes.filter(i => i.id !== id);
    guardarHistorialEnStorage();
    cargarHistorialImagenes();

    mostrarAlerta('Registro eliminado del historial', 'success');
}

// ==================== OPORTUNIDADES ====================

function abrirFormulario() {
    document.getElementById('formularioModal').classList.add('active');
    document.getElementById('formOportunidad').reset();
}

function cerrarFormulario() {
    document.getElementById('formularioModal').classList.remove('active');
    document.getElementById('formOportunidad').reset();
}

function registrarOportunidad(event) {
    event.preventDefault();

    const cliente = document.getElementById('cliente').value.trim();
    const producto = document.getElementById('producto').value.trim();
    const cantidad = parseInt(document.getElementById('cantidad').value);

    if (!cliente || !producto || !cantidad) {
        mostrarAlerta('Cliente, producto y cantidad son obligatorios', 'warning');
        return;
    }

    const payload = {
        cliente: cliente,
        producto: producto,
        cantidad: cantidad
    };

    fetch(`${API_URL}/registrar-oportunidad`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
        .then(response => {
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            return response.json();
        })
        .then(data => {
            const mensaje = data.mensaje || "";

            if (mensaje.toLowerCase().includes("no se registro")) {
                mostrarAlerta(mensaje, 'error');
            } else {
                mostrarAlerta('Oportunidad registrada correctamente', 'success');
                cerrarFormulario();
                cargarOportunidades();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta(`Error al registrar: ${error.message}`, 'error');
        });
}

function cargarOportunidades() {
    fetch(`${API_URL}/oportunidades`)
        .then(response => {
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            return response.json();
        })
        .then(data => {
            mostrarOportunidades(data.oportunidades);
        })
        .catch(error => {
            console.error('Error al cargar oportunidades:', error);
            const tbody = document.getElementById('opportunitiesBody');
            tbody.innerHTML = '<tr><td colspan="7" class="empty-table">Error al cargar oportunidades</td></tr>';
        });
}

function mostrarOportunidades(contenido) {
    const tbody = document.getElementById('opportunitiesBody');

    if (!contenido || contenido.trim() === '' || contenido.includes('No hay oportunidades')) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-table">No hay oportunidades registradas</td></tr>';
        document.getElementById('totalOpportunidades').textContent = '0';
        return;
    }

    const lineas = contenido.split('\n').filter(linea => linea.trim() && (linea.includes('OPP-') || linea.includes('**OPP')));

    if (lineas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-table">No hay oportunidades registradas</td></tr>';
        document.getElementById('totalOpportunidades').textContent = '0';
        return;
    }

    const html = lineas.map((linea) => {
        // FORMATO 1: OPP-0001 | timestamp | cliente=... | producto=... | estado=...
        // FORMATO 2: **OPP-0001**: cliente: ... | Producto: ... | Estado: ...

        let id = 'N/A';
        let cliente = 'N/A';
        let producto = 'N/A';
        let cantidad = '0';
        let monto = '0.00';
        let estado = 'abierta';

        // Detectar formato y parsear
        if (linea.includes('**OPP')) {
            // FORMATO 2 (nuevo del orquestador)
            const matchId = linea.match(/\*\*OPP-(\d+)\*\*/);
            if (matchId) id = `OPP-${matchId[1]}`;

            // Parsear campos con ":" (cliente: value)
            const campos = linea.split('|');
            campos.forEach(campo => {
                if (campo.includes('cliente:')) {
                    cliente = campo.split(':')[1]?.trim() || 'N/A';
                } else if (campo.includes('Producto:')) {
                    producto = campo.split(':')[1]?.trim() || 'N/A';
                } else if (campo.includes('Cantidad:')) {
                    cantidad = campo.split(':')[1]?.trim() || '0';
                } else if (campo.includes('Monto') || campo.includes('Total:')) {
                    monto = campo.split(':')[1]?.trim() || '0.00';
                } else if (campo.includes('Estado:')) {
                    estado = campo.split(':')[1]?.trim().toLowerCase() || 'abierta';
                }
            });
        } else {
            // FORMATO 1 (del archivo)
            const partes = linea.split('|').map(p => p.trim());

            if (partes.length >= 2) {
                id = partes[0];

                for (let i = 2; i < partes.length; i++) {
                    const campo = partes[i];
                    if (campo.includes('cliente=')) {
                        cliente = campo.split('=')[1];
                    } else if (campo.includes('producto=')) {
                        producto = campo.split('=')[1];
                    } else if (campo.includes('cantidad=')) {
                        cantidad = campo.split('=')[1];
                    } else if (campo.includes('monto_total=')) {
                        monto = campo.split('=')[1];
                    } else if (campo.includes('estado=')) {
                        estado = campo.split('=')[1].toLowerCase();
                    }
                }
            }
        }

        // Validar estado
        if (!['abierta', 'ganada', 'perdida'].includes(estado)) {
            estado = 'abierta';
        }

        const badgeClass = `badge-${estado}`;

        // Monto: mostrar "Pendiente" si aún no tiene cierre (N/A o no numérico)
        const montoTexto = (monto === 'N/A' || isNaN(parseFloat(monto)))
            ? 'Pendiente'
            : 'USD ' + parseFloat(monto).toFixed(2);

        return `
            <tr>
                <td><strong>${escapeHtml(id)}</strong></td>
                <td>${escapeHtml(cliente)}</td>
                <td>${escapeHtml(producto)}</td>
                <td>${escapeHtml(cantidad)}</td>
                <td>${montoTexto}</td>
                <td><span class="badge ${badgeClass}">${estado.toUpperCase()}</span></td>
                <td>
                    <button class="btn btn-sm" onclick="abrirModalCambiarEstado('${id}', '${escapeHtml(cliente)}', '${escapeHtml(producto)}', ${parseInt(cantidad) || 0})">
                        Cambiar
                    </button>
                </td>
            </tr>
        `;
    }).join('');

    tbody.innerHTML = html || '<tr><td colspan="7" class="empty-table">No hay oportunidades válidas</td></tr>';
    document.getElementById('totalOpportunidades').textContent = lineas.length;
}

function abrirModalCambiarEstado(id, cliente, producto, cantidad) {
    oportunidadParaCambiarEstado = id;
    document.getElementById('oppIdDisplay').textContent = id;
    document.getElementById('oppClienteDisplay').textContent = cliente;
    document.getElementById('oppProductoDisplay').textContent = producto;
    document.getElementById('cambiarEstadoModal').classList.add('active');

    // Resetear selección y campos de cierre cada vez que se abre
    document.getElementById('nuevoEstado').value = 'abierta';
    document.getElementById('camposCierre').style.display = 'none';
    document.getElementById('cierreCantidad').value = cantidad || 0;
    document.getElementById('cierreDescuento').value = 0;
    document.getElementById('cierrePrecioDescuento').value = '';
    document.getElementById('cierreMontoTotal').value = '';
    document.getElementById('cierreCondicionPago').value = '';
    document.getElementById('cierreOrdenCompra').value = '';
    document.getElementById('cierreDatosFacturacion').value = '';
    document.getElementById('cierreFechaCierre').value = '';
    document.getElementById('cierreFechaEntrega').value = '';

    // Consultar precio de lista real desde el catálogo
    const inputPrecio = document.getElementById('cierrePrecioUnitario');
    inputPrecio.value = '';
    inputPrecio.placeholder = 'Consultando precio en catálogo...';
    inputPrecio.disabled = true;

    consultarPrecioCatalogo(producto)
        .then(precio => {
            inputPrecio.disabled = false;
            if (precio !== null) {
                inputPrecio.value = precio;
                inputPrecio.placeholder = '';
                calcularMontoCierre();
            } else {
                inputPrecio.placeholder = 'No se encontró precio, ingrésalo manualmente';
            }
        })
        .catch(error => {
            console.error('Error al consultar precio:', error);
            inputPrecio.disabled = false;
            inputPrecio.placeholder = 'Error al consultar, ingrésalo manualmente';
        });
}

function consultarPrecioCatalogo(producto) {
    return fetch(`${API_URL}/consultar`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            pregunta: `¿Cuál es el precio de lista de ${producto}?`
        })
    })
        .then(response => {
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            return response.json();
        })
        .then(data => {
            const respuesta = data.respuesta || '';
            // Busca un patron tipo "USD 1,299" o "USD 1299.00"
            const match = respuesta.match(/USD\s*([\d,]+(?:\.\d+)?)/i);

            if (match) {
                const numeroLimpio = match[1].replace(/,/g, '');
                return parseFloat(numeroLimpio);
            }

            return null;
        });
}

function cerrarModalEstado() {
    document.getElementById('cambiarEstadoModal').classList.remove('active');
    oportunidadParaCambiarEstado = null;
}

function mostrarCamposCierre() {
    const nuevoEstado = document.getElementById('nuevoEstado').value;
    const camposCierre = document.getElementById('camposCierre');

    camposCierre.style.display = (nuevoEstado === 'ganada') ? 'block' : 'none';
}

function calcularMontoCierre() {
    const cantidad = parseFloat(document.getElementById('cierreCantidad').value) || 0;
    const precioUnitario = parseFloat(document.getElementById('cierrePrecioUnitario').value) || 0;
    const descuento = parseFloat(document.getElementById('cierreDescuento').value) || 0;

    const precioConDescuento = precioUnitario * (1 - descuento / 100);
    const montoTotal = cantidad * precioConDescuento;

    document.getElementById('cierrePrecioDescuento').value = precioConDescuento.toFixed(2);
    document.getElementById('cierreMontoTotal').value = montoTotal.toFixed(2);
}

function guardarCambioEstado() {
    if (!oportunidadParaCambiarEstado) return;

    const nuevoEstado = document.getElementById('nuevoEstado').value;

    const payload = {
        id_oportunidad: oportunidadParaCambiarEstado,
        nuevo_estado: nuevoEstado
    };

    if (nuevoEstado === 'ganada') {
        const precioConDescuento = document.getElementById('cierrePrecioDescuento').value;
        const condicion = document.getElementById('cierreCondicionPago').value;
        const monto = document.getElementById('cierreMontoTotal').value;
        const orden = document.getElementById('cierreOrdenCompra').value;
        const facturacion = document.getElementById('cierreDatosFacturacion').value;
        const fechaCierre = document.getElementById('cierreFechaCierre').value;
        const fechaEntrega = document.getElementById('cierreFechaEntrega').value;

        if (!precioConDescuento || !condicion || !monto || !orden || !facturacion || !fechaCierre || !fechaEntrega) {
            mostrarAlerta('Para marcar como ganada, completa todos los datos de cierre', 'warning');
            return;
        }

        payload.precio_con_descuento = parseFloat(precioConDescuento);
        payload.condicion_pago = condicion;
        payload.monto_total = parseFloat(monto);
        payload.orden_compra = orden;
        payload.datos_facturacion = facturacion;
        payload.fecha_cierre = fechaCierre;
        payload.fecha_entrega = fechaEntrega;
    }

    fetch(`${API_URL}/actualizar-oportunidad`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
        .then(response => {
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            return response.json();
        })
        .then(data => {
            const mensaje = data.mensaje || "";

            if (mensaje.toLowerCase().includes("no se puede marcar")) {
                mostrarAlerta(mensaje, 'error');
            } else {
                mostrarAlerta(`Estado actualizado a: ${nuevoEstado}`, 'success');
                cerrarModalEstado();
            }

            setTimeout(() => {
                cargarOportunidades();
            }, 500);
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta(`Error al actualizar: ${error.message}`, 'error');
        });
}

// ==================== UTILIDADES ====================

function mostrarAlerta(mensaje, tipo = 'info') {
    const div = document.createElement('div');
    div.className = `alert alert-${tipo}`;
    div.textContent = mensaje;

    document.body.appendChild(div);

    setTimeout(() => {
        div.remove();
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

window.addEventListener('click', function (event) {
    const modalForm = document.getElementById('formularioModal');
    const modalEstado = document.getElementById('cambiarEstadoModal');

    if (event.target === modalForm) {
        cerrarFormulario();
    }
    if (event.target === modalEstado) {
        cerrarModalEstado();
    }
});