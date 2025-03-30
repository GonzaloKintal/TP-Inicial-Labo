// Desactivar el botón de entrenar modelo inicialmente
const trainModelBtn = document.getElementById('train_model');
trainModelBtn.disabled = true;

// Modificar el evento del botón "Generar Dataset"
document.getElementById('generate-dataset').addEventListener('click', function(event) {
    event.preventDefault();
    
    // Mostrar indicador de carga
    const generateBtn = this;
    const originalText = generateBtn.textContent;
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="flex items-center justify-center"><svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Generando dataset...</span>';
    
    // Crear una promesa que se resuelve después de 2 segundos
    const minimumLoadTime = new Promise(resolve => setTimeout(resolve, 2000));
    
    // Combinar con la petición fetch
    Promise.all([
        fetch(DJANGO_CONFIG.generateDatasetUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': DJANGO_CONFIG.csrfToken,
            },
            body: JSON.stringify({})
        }),
        minimumLoadTime
    ])
    .then(([response]) => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        // Habilitar el botón de entrenar modelo
        trainModelBtn.disabled = false;
        trainModelBtn.classList.remove('bg-gray-400');
        trainModelBtn.classList.add('bg-green-600', 'hover:bg-green-700');
        
        // Actualizar la tabla con los nuevos datos
        updateDatasetTable(data.dataset);
    })
    .catch(error => {
        console.error('Error:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4';
        errorDiv.textContent = 'Error al generar el dataset: ' + error.message;
        document.querySelector('#dataset .max-w-6xl').prepend(errorDiv);
    })
    .finally(() => {
        generateBtn.disabled = false;
        generateBtn.textContent = originalText;
    });
});

// Función para actualizar la tabla con los nuevos datos
function updateDatasetTable(dataset) {
    const tbody = document.querySelector('#dataset-table tbody');
    tbody.innerHTML = '';
    
    if (dataset && dataset.length > 0) {
        dataset.forEach(item => {
            const row = document.createElement('tr');
            
            // Determinar clases CSS según el tipo de trabajo y riesgo
            const workClass = item.Tipo_de_Trabajo === 'Físico' ? 'physical-work' : 'office-work';
            const riskClass = item.Riesgo === 1 ? 'risk-high' : 'risk-low';
            const riskText = item.Riesgo === 1 ? 'Alto Riesgo' : 'Bajo Riesgo';
            
            row.innerHTML = `
                <td class="px-6 py-4 text-center">${item.ID}</td>
                <td class="px-6 py-4 text-center">${item.Edad}</td>
                <td class="px-6 py-4 text-center">${item.Horas_Trabajadas_Por_Semana}</td>
                <td class="px-6 py-4 text-center">${item.Ausencias_Por_Enfermedad}</td>
                <td class="px-6 py-4 text-center">${item.Nivel_de_Estres}</td>
                <td class="px-6 py-4 text-center ${workClass}">${item.Tipo_de_Trabajo}</td>
                <td class="px-6 py-4 text-center ${riskClass}">${riskText}</td>
            `;
            
            tbody.appendChild(row);
        });
        
        // Actualizar contador de registros
        document.querySelector('.p-4.bg-gray-50.border-b span').textContent = `${dataset.length} registros`;
    } else {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-4 text-center text-gray-500">No hay datos disponibles. Genera un dataset.</td>
            </tr>
        `;
    }
}

// Código para entrenar el modelo (también con tiempo mínimo de carga)
document.getElementById('train_model').addEventListener('click', function(event) {
    event.preventDefault();
    
    const loader = document.getElementById('precision-loader');
    const precisionValue = document.getElementById('precision-value');
    const precisionText = precisionValue.nextElementSibling;
    
    loader.classList.remove('hidden');
    precisionValue.classList.add('hidden');
    precisionText.classList.add('hidden');
    
    const minimumLoadTime = new Promise(resolve => setTimeout(resolve, 2000));
    
    Promise.all([
        fetch(DJANGO_CONFIG.trainModelUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': DJANGO_CONFIG.csrfToken,
            },
            body: JSON.stringify({})
        }),
        minimumLoadTime
    ])
    .then(([response]) => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        loader.classList.add('hidden');
        precisionValue.classList.remove('hidden');
        precisionText.classList.remove('hidden');
       precisionValue.innerText = `${data.precision}%`;
    })
    .catch(error => {
        console.error('Error:', error);
        loader.classList.add('hidden');
        precisionValue.classList.remove('hidden');
        precisionText.classList.remove('hidden');
        precisionValue.innerText = 'Error';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4';
        errorDiv.textContent = 'Error al entrenar el modelo: ' + error.message;
        document.querySelector('#modelo .max-w-6xl').prepend(errorDiv);
    });
});


document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.sortable-header').forEach(header => {
        header.addEventListener('click', function(e) {
            e.preventDefault();
            const columnIndex = parseInt(this.getAttribute('data-column'));
            ordenarPorColumna(e, columnIndex);
        });
    });
});

let ordenAscendente = [true, true, true, true, true, true, true];  // Mantiene el estado de cada columna (ascendente o descendente)

// function ordenarPorColumna(event, columnaIndex) {
//     event.preventDefault();  // Prevenir que la página se desplace hacia arriba

//     const tabla = document.querySelector("#dataset-table tbody");
//     const filas = Array.from(tabla.rows);

//     // Ordenar las filas
//     filas.sort(function(a, b) {
//         const celdaA = a.cells[columnaIndex].textContent.trim();
//         const celdaB = b.cells[columnaIndex].textContent.trim();

//         if (columnaIndex === 1 || columnaIndex === 2 || columnaIndex === 3 || columnaIndex === 4) {
//             // Si son números (Edad, Horas, Ausencias, Estres), convertimos a números
//             return ordenAscendente[columnaIndex]
//                 ? parseFloat(celdaA) - parseFloat(celdaB)
//                 : parseFloat(celdaB) - parseFloat(celdaA);
//         } else {
//             // Si son cadenas (Tipo de trabajo, Riesgo), los comparamos como texto
//             return ordenAscendente[columnaIndex]
//                 ? celdaA.localeCompare(celdaB)
//                 : celdaB.localeCompare(celdaA);
//         }
//     });

//     // Insertamos las filas ordenadas
//     filas.forEach(function(fila) {
//         tabla.appendChild(fila);
//     });

//     // Alternamos el estado de la columna (ascendente/descendente)
//     ordenAscendente[columnaIndex] = !ordenAscendente[columnaIndex];
// }
function ordenarPorColumna(event, columnaIndex) {
    event.preventDefault();
    
    const tabla = document.querySelector("#dataset-table");
    const tbody = tabla.querySelector("tbody");
    const filas = Array.from(tbody.rows);

    filas.sort(function(a, b) {
        const celdaA = a.cells[columnaIndex].textContent.trim();
        const celdaB = b.cells[columnaIndex].textContent.trim();

        // Columnas numéricas: ID (0), Edad (1), Horas (2), Ausencias (3), Estrés (4)
        if (columnaIndex === 0 || columnaIndex === 1 || columnaIndex === 2 || columnaIndex === 3 || columnaIndex === 4) {
            const numA = parseFloat(celdaA) || 0; // Si falla parseFloat, usa 0
            const numB = parseFloat(celdaB) || 0;
            return ordenAscendente[columnaIndex] ? numA - numB : numB - numA;
        } else {
            // Columnas de texto: Trabajo (5), Riesgo (6)
            return ordenAscendente[columnaIndex] 
                ? celdaA.localeCompare(celdaB) 
                : celdaB.localeCompare(celdaA);
        }
    });

    // Limpiar y reinsertar filas
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    filas.forEach(fila => tbody.appendChild(fila));

    // Cambiar el estado de orden
    ordenAscendente[columnaIndex] = !ordenAscendente[columnaIndex];

    // Opcional: Actualizar indicadores visuales
    actualizarIndicadoresOrden(columnaIndex);
}

function actualizarIndicadoresOrden(columnaIndex) {
    document.querySelectorAll('.sortable-header').forEach(header => {
        // Obtenemos solo el texto original (sin las flechas anteriores)
        const textoOriginal = header.getAttribute('data-original-text') || header.textContent;
        header.innerHTML = textoOriginal; // Restablecemos a solo texto
        header.setAttribute('data-original-text', textoOriginal); // Guardamos el texto original
    });
    
    const headerActual = document.querySelector(`.sortable-header[data-column="${columnaIndex}"]`);
    if (headerActual) {
        const textoOriginal = headerActual.getAttribute('data-original-text') || headerActual.textContent;
        const flecha = ordenAscendente[columnaIndex] ? ' ↑' : ' ↓';
        headerActual.innerHTML = textoOriginal + flecha;
    }
}