# Patito S.A. — Mesa de Ayuda IA para Ventas

Prototipo de mesa de ayuda con **agentes especializados LangChain + Google Gemini** para el Departamento de Ventas de Patito S.A. (datos ficticios).

El usuario pregunta en lenguaje natural, un **agente orquestador** decide qué herramienta(s) invocar, y devuelve una respuesta consolidada, trazable y basada **únicamente** en la base documental entregada.

El proyecto está dividido en dos partes independientes:

```
Proyecto_Patito_SA/
├── backend/     ← API REST + agentes LangChain + Gemini
├── frontend/    ← interfaz web (HTML/CSS/JS vanilla)
├── .gitignore
└── README.md    ← este archivo
```

---

## 1. Stack tecnológico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.10+ |
| Framework de agentes | LangChain + LangGraph |
| LLM | Google Gemini `gemini-3.1-flash-lite` vía `ChatGoogleGenerativeAI` |
| Embeddings | Google Gemini `gemini-embedding-001` vía `GoogleGenerativeAIEmbeddings` |
| Vector store | ChromaDB (un índice persistente por agente) |
| API REST | FastAPI + Uvicorn |
| Frontend | HTML / CSS / JavaScript vanilla |
| Pruebas | pytest |

---

## 2. Arquitectura

```
                      ┌──────────────────┐
   Frontend (HTML/JS) │  index.html      │
   localhost:3000     └────────┬─────────┘
                                │ HTTP / JSON  (fetch a http://localhost:8000)
                       ┌────────▼────────┐
   API REST            │    main.py      │  FastAPI (CORS abierto)
   localhost:8000       └────────┬────────┘
                                 │
                       ┌─────────▼───────────┐
   Orquestador          │ src/orquestador.py  │  create_agent + InMemorySaver
                        └─────────┬───────────┘
                                  │ decide tool(s) según SYSTEM_PROMPT
        ┌──────────────┬─────────┴───────┬──────────────┬───────────────┐
        ▼              ▼                 ▼              ▼               ▼
  consultar_      consultar_       consultar_     analizar_      registrar_ /
  catalogo        politicas        proceso_crm    imagen_        obtener_ /
     │                │                 │         producto       actualizar_
     ▼                ▼                 ▼              │         oportunidad
  Chroma           Chroma            Chroma         Gemini             │
  /catalogo       /politicas       /proceso_crm     Vision             ▼
                                                               registro_
                                                         oportunidades.txt
```

### Roles por archivo (dentro de `backend/`)

| Componente | Responsabilidad |
|---|---|
| `src/config.py` | Carga `.env`, define rutas, modelos Gemini y `TOP_K`. Falla temprano si no hay API key |
| `src/ingestion/build_indexes.py` | TXT → chunking por sección → embeddings → Chroma. Un índice por agente |
| `src/tools/catalogo_tools.py` | RAG sobre catálogo y precios |
| `src/tools/politicas_tools.py` | RAG sobre descuentos, crédito, garantías y devoluciones |
| `src/tools/proceso_crm_tools.py` | RAG sobre embudo de ventas y requisitos del CRM |
| `src/tools/imagen_tools.py` | Agente multimodal: identifica y extrae información impresa en imágenes (base64) con Gemini Vision |
| `src/tools/accion_tools.py` | Agente de acción: registra, consulta y actualiza oportunidades en un archivo de texto |
| `src/orquestador.py` | Agente LangChain único que enruta a las tools y consolida la respuesta |
| `main.py` | Capa REST (FastAPI) que expone el orquestador y los agentes adicionales |

### Rol del frontend (`frontend/`)

| Archivo | Responsabilidad |
|---|---|
| `index.html` | Estructura de la interfaz: consultas, análisis de imagen, tabla de oportunidades |
| `style.css` | Estilos visuales |
| `script.js` | Toda la lógica de conexión con la API (`fetch` a `http://localhost:8000`), manejo de formularios, cálculo de montos, historial de imágenes |

---

## 3. Estructura completa del proyecto

```
Proyecto_Patito_SA/
├── backend/
│   ├── main.py                        # API REST (FastAPI)
│   ├── requirements.txt
│   ├── .env.example                   # Plantilla SIN credenciales reales
│   ├── src/
│   │   ├── config.py                  # Configuración global (modelos, TOP_K, rutas)
│   │   ├── orquestador.py             # Agente orquestador
│   │   ├── ingestion/
│   │   │   └── build_indexes.py       # Generación de índices vectoriales
│   │   └── tools/
│   │       ├── catalogo_tools.py
│   │       ├── politicas_tools.py
│   │       ├── proceso_crm_tools.py
│   │       ├── imagen_tools.py
│   │       └── accion_tools.py
│   ├── data/
│   │   ├── 01_Catalogo_Productos_Precios.txt
│   │   ├── 02_Politicas_Comerciales_Descuentos_Credito.txt
│   │   ├── 03_Proceso_Ventas_CRM.txt
│   │   ├── imagenes_prueba/           # Imágenes de prueba para el agente multimodal
│   │   └── imagenes_consultadas/      # Imágenes analizadas (se autogenera)
│   ├── vectorstores/                  # Índices Chroma (se autogenera, NO se versiona)
│   │   ├── catalogo/
│   │   ├── politicas/
│   │   └── proceso_crm/
│   ├── test/
│   │   ├── test_build_indexes.py
│   │   ├── test_accion_tools.py
│   │   ├── test_imagen_generator.py
│   │   ├── test_imagen_tools.py
│   │   ├── test_orquestador.py
│   │   └── test_api.py
│   ├── registro_oportunidades.txt     # Salida del agente de acción (NO se versiona)
│   └── imagenes_historial.txt         # Bitácora de imágenes analizadas
│
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```

---

## 4. Instalación

### 4.1 Clonar el repositorio

```powershell
git clone https://github.com/AdrianPozoT/Proyecto-Semillero.git
cd Proyecto-Semillero
```

### 4.2 Crear y activar el entorno virtual (dentro de `backend/`)

El entorno virtual vive **dentro de `backend/`**, no en la raíz del proyecto — el frontend no necesita Python.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate.bat
```

> En PowerShell, si `Activate.ps1` da error de política de ejecución:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
> Alternativa sin cambiar políticas: usar `.venv\Scripts\activate.bat`.

Linux / macOS:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### 4.3 Instalar dependencias

```powershell
pip install -r requirements.txt
```

**Si aparece un error de certificado SSL** (`CERTIFICATE_VERIFY_FAILED: self-signed certificate in certificate chain`), es común en redes de instituciones, oficinas o con antivirus que inspeccionan tráfico HTTPS. Solución:
> ```powershell
> pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
> ```

---

## 5. Configuración de la API Key de Google Gemini

### 5.1 Obtener la key (si aún no tienes una)

1. Entrar a **https://aistudio.google.com/apikey**
2. Iniciar sesión con una cuenta de Google.
3. Clic en **Create API key** → seleccionar o crear un proyecto de Google Cloud.
4. Copiar la key generada (formato `AIza...`).

El nivel gratuito de Google AI Studio es suficiente para este prototipo.

### 5.2 Configurar el archivo `.env` (dentro de `backend/`)

```powershell
# Estando dentro de backend/
copy .env.example .env
```

Editar `backend/.env` y pegar la key:

```
GOOGLE_API_KEY=AIza...tu_clave_aqui
```

Contenido de `.env.example` (plantilla versionada, sin credenciales):

```
GOOGLE_API_KEY=tu_api_key_aqui
```

> **Importante:** `.env` está en `.gitignore` y **nunca** debe subirse a GitHub.
> Si se sube por error, GitHub bloquea el push (protección de secretos) y la key
> debe revocarse en AI Studio y generarse de nuevo.

`src/config.py` valida la key al importarse y lanza un error con instrucciones si falta.

---

## 6. Orden de ejecución

El orden importa: sin índices vectoriales, los agentes RAG no pueden responder.

### Paso 1 — Generar los índices vectoriales (obligatorio, primera vez)

Desde `backend/`, con el entorno virtual activado:

```powershell
python -m src.ingestion.build_indexes
```

Salida esperada:

```
[catalogo] Indexando 01_Catalogo_Productos_Precios.txt...
  -> 4 chunks generados para 'catalogo'.
[politicas] Indexando 02_Politicas_Comerciales_Descuentos_Credito.txt...
  -> 5 chunks generados para 'politicas'.
[proceso_crm] Indexando 03_Proceso_Ventas_CRM.txt...
  -> 5 chunks generados para 'proceso_crm'.
Todos los indices generados.
```

Esto crea `backend/vectorstores/catalogo/`, `backend/vectorstores/politicas/` y `backend/vectorstores/proceso_crm/`.

> **Por qué es el primer paso:** cada documento se divide en chunks por sección
> numerada (los documentos ya vienen así, redactados con secciones tipo
> "1. Descuentos", "2. Condiciones de crédito"); cada chunk se convierte en un
> vector con los embeddings de Gemini y se guarda en Chroma. Sin este paso, el
> retriever no tiene nada que buscar y los agentes responden "No encontré
> información suficiente" a cualquier pregunta.
>
> Debe re-ejecutarse **cada vez que se modifique un documento** de `data/`, o si
> se cambia el modelo de embeddings en `config.py`. `vectorstores/` no se
> versiona en Git: cada persona que clona el repo debe generarlo localmente.

### Paso 2 — Ejecutar las pruebas (opcional, recomendado)

Desde `backend/`:

```powershell
python -m pytest test/test_accion_tools.py -v -s
python -m pytest test/test_imagen_tools.py -v -s
python -m pytest test/test_orquestador.py -v -s
python -m pytest test/test_api.py -v -s

# Todo junto
python -m pytest test/ -v
```

> **Siempre usar `python -m`.** Ejecutar `python test/test_x.py` directamente
> produce `ModuleNotFoundError: No module named 'src'`, porque Python no agrega
> la raíz de `backend/` al `sys.path`. El flag `-m` sí lo hace.
>
> Las pruebas del orquestador y del agente multimodal consumen cuota real de la
> API de Gemini (no usan mocks).

### Paso 3 — Levantar el backend

**Abre una terminal nueva** dedicada exclusivamente al backend (no reutilices la que usaste para generar los índices o correr las pruebas, para no perder de vista sus logs):

```powershell
cd backend
.venv\Scripts\activate.bat
python main.py
```

Salida esperada:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Deja esta terminal abierta y corriendo mientras uses el sistema.** No le des `Ctrl+C` ni la cierres — si lo haces, el frontend dejará de poder conectarse y las peticiones fallarán con `ERR_CONNECTION_REFUSED`.

Verificación rápida en el navegador: `http://localhost:8000/health` → debe responder `{"status": "ok", ...}`.
Documentación interactiva (Swagger): `http://localhost:8000/docs`.

### Paso 4 — Levantar el frontend

**Abre una segunda terminal nueva**, distinta a la del backend (por ejemplo, con el botón "+" o "Split Terminal" del panel de terminal en VS Code, o `Ctrl+Shift+` \` para una terminal nueva):

```powershell
cd frontend
python -m http.server 3000
```

Esta terminal también se queda "colgada" mostrando los logs de peticiones — es el comportamiento normal, no cerrarla mientras se usa el frontend.

Abrir en el navegador: **`http://localhost:3000/index.html`**

> El frontend se conecta a `http://localhost:8000` (constante `API_URL` en
> `script.js`). Si se cambia el puerto del backend, actualizar esa constante.
> No abrir `index.html` con doble clic (`file://`): el navegador bloquea las
> peticiones por CORS. Debe servirse siempre con `python -m http.server` (o
> equivalente), nunca abriéndolo directo desde el explorador de archivos.

### Resumen: dos terminales, siempre abiertas en paralelo

| Terminal | Comando | ¿Se cierra? |
|---|---|---|
| Terminal 1 (backend) | `cd backend` → activar venv → `python main.py` | No, mientras se use el sistema |
| Terminal 2 (frontend) | `cd frontend` → `python -m http.server 3000` | No, mientras se use el sistema |

Si alguna de las dos se detiene (cierre accidental de la terminal, `Ctrl+C`, reinicio de VS Code), hay que volver a levantarla antes de seguir probando — de lo contrario el frontend mostrará errores de conexión o se quedará "cargando" indefinidamente sin explicación visible en pantalla.

---

## 7. Endpoints de la API

| Método | Ruta | Body | Descripción |
|---|---|---|---|
| `POST` | `/consultar` | `{pregunta, thread_id?}` | Consulta en lenguaje natural al orquestador |
| `POST` | `/analizar-imagen` | `{imagen_base64, descripcion?, thread_id?}` | Analiza una imagen y, si corresponde, cruza el producto identificado con catálogo y/o políticas |
| `POST` | `/registrar-oportunidad` | `{cliente, producto, cantidad}` | Registra una oportunidad con los datos mínimos del embudo |
| `POST` | `/actualizar-oportunidad` | `{id_oportunidad, nuevo_estado, ...datos de cierre}` | Cambia el estado (abierta / ganada / perdida); para "ganada" valida los datos de cierre |
| `GET` | `/oportunidades` | — | Lista todas las oportunidades registradas |
| `GET` | `/health` | — | Verificación de disponibilidad |

Ejemplo:

```powershell
curl -X POST http://localhost:8000/consultar `
  -H "Content-Type: application/json" `
  -d "{\"pregunta\": \"Cual es el precio del Patito Pro 2026?\"}"
```

---

## 8. Flujo de la solución

1. El usuario envía una pregunta (frontend o API).
2. `main.py` la pasa a `consultar()` del orquestador.
3. El orquestador (`create_agent`) evalúa la pregunta contra su `SYSTEM_PROMPT` y las **docstrings de cada tool**, y decide cuál(es) invocar, formulando una sub-pregunta específica para cada una (para no degradar la búsqueda semántica de cada agente).
4. Cada tool RAG ejecuta `retriever.invoke(sub_pregunta)` sobre **su propio** índice Chroma.
5. La tool arma el contexto y llama al LLM con un prompt que prohíbe usar conocimiento externo.
6. La tool devuelve la respuesta con su etiqueta de trazabilidad: `[Fuente: Catálogo | Secciones: 1. LÍNEA PATITO PRO]`.
7. El orquestador consolida las respuestas parciales y agrupa las fuentes en un bloque final **Fuentes consultadas**.
8. La API responde en JSON, aplanando previamente cualquier estructura de bloques que Gemini pueda devolver en lugar de texto plano.

### Caso con imagen (agente multimodal)

El frontend convierte el archivo a base64 y lo envía a `/analizar-imagen`. La tool `analizar_imagen_producto` identifica el tipo de documento (producto, cotización o lista de precios), extrae lo impreso, guarda el archivo en `data/imagenes_consultadas/` y registra el resultado en `imagenes_historial.txt`. Si la descripción de la consulta pide confirmar precio, disponibilidad, descuento o crédito, `main.py` invoca además `consultar_catalogo` y/o `consultar_politicas` con el nombre de producto identificado, para verificar esa información contra la base documental oficial.

**Imágenes de prueba disponibles** en `backend/data/imagenes_prueba/`:
- `Patito_pro_2026.jpg`, `Patito_lite_mini.png` — fichas de producto
- `Cargador_rápido_65w.png`, `Funda_protectora.png`, `Mouse_inalambrico_patito.png` — accesorios
- `cotizacion_patito_s.a.png`, `lista_de_precios_patito_s.a.png` — documentos comerciales reales
- `producto.png`, `cotizacion.png`, `lista_precios.png` — imágenes sintéticas generadas con `test_imagen_generator.py`, para tener siempre datos de prueba disponibles aunque no se suban imágenes reales

### Caso con acción (agente de acción)

El registro de una oportunidad ocurre en dos momentos, según el Manual del Proceso de Ventas y CRM:

- **Registro inicial:** `registrar_oportunidad` solo exige cliente, producto y cantidad. Genera un ID incremental (`OPP-0001`), fecha y hora, y guarda la oportunidad con `estado=abierta` en `registro_oportunidades.txt`.
- **Cierre como ganada:** `actualizar_oportunidad` valida que existan orden de compra, datos de facturación, precio con descuento, condición de pago, monto total, fecha de cierre y fecha de entrega. Si falta alguno, no cambia el estado y lo indica explícitamente. Marcar como "perdida" no requiere estos datos adicionales.

El archivo `backend/registro_oportunidades.txt` se genera automáticamente al registrar la primera oportunidad, con líneas en formato:

```
OPP-0001 | 2026-07-25 10:03:09 | cliente=Comercial ABC S.A | producto=Patito Pro Max 2026 | cantidad=4 | ... | estado=abierta
```

### Fuera de alcance

Si la consulta no pertenece al dominio de Patito S.A., el orquestador no invoca ninguna tool y responde con un mensaje de rechazo explícito, sin bloque de fuentes.

---

## 9. Ejemplos de preguntas y respuestas esperadas

| # | Pregunta | Agente(s) esperado(s) | Respuesta esperada |
|---|---|---|---|
| 1 | ¿Cuál es el precio de lista y la disponibilidad del Patito Pro 2026? | Catálogo | USD 1,299 — EN STOCK, con etiqueta de fuente |
| 2 | ¿Qué descuento máximo puedo ofrecer a un cliente nuevo sin aprobación del gerente? | Políticas | Hasta 10%, con etiqueta de fuente |
| 3 | ¿Qué debo registrar antes de marcar una oportunidad como ganada? | Proceso CRM | Orden de compra, datos de facturación, precios finales, condición de pago, monto total, fecha de cierre y de entrega |
| 4 | **(mixta, 3 documentos)** Un cliente nuevo quiere 50 unidades del Patito Pro 2026 a crédito con descuento especial. ¿Cuál es el precio, qué descuento puedo ofrecer, las condiciones de crédito, y qué debo registrar en el CRM? | Catálogo + Políticas + Proceso CRM | Respuesta consolidada citando las **tres** fuentes: precio de lista (USD 1,299), nivel de descuento autorizable (hasta 10% directo), condición de crédito (primera compra de contado), y campos a registrar en el CRM |
| 5 | ¿Cuál es la capital de Francia? | Ninguno | Mensaje de rechazo por estar fuera del alcance de Patito S.A. |
| 6 | **(imagen)** Adjunto la foto de un producto: ¿cuál es, cuál es su precio de lista y está disponible? | Multimodal + Catálogo | Identificación del producto desde la imagen, y confirmación de precio/disponibilidad verificada en catálogo |
| 7 | **(acción)** Registra una oportunidad: cliente Comercial ABC, producto Patito Pro 2026, cantidad 10 | Acción | Confirmación con ID de oportunidad generado (ej. `OPP-0001`) |
| 8 | **(acción)** Marca la oportunidad OPP-0001 como ganada, con todos los datos de cierre | Acción | Confirmación del cambio de estado, actualiza `registro_oportunidades.txt` |
| 9 | **(acción, datos incompletos)** Marca la oportunidad OPP-0002 como ganada, sin datos de cierre | Acción | Rechazo explícito indicando qué campos faltan, sin cambiar el estado |

---

## 10. Manejo de errores

| Escenario | Comportamiento |
|---|---|
| Falta `GOOGLE_API_KEY` | Error al importar `config.py`, con instrucciones para configurarla |
| Vector store no generado | El retriever devuelve vacío → mensaje de "sin información suficiente" |
| Fallo de la API de Gemini | Se captura la excepción y se devuelve un mensaje de error técnico, sin tumbar el servidor |
| Imagen mal codificada | `analizar_imagen_producto` valida el base64 y retorna un mensaje de error legible |
| Datos incompletos al registrar | No escribe en el archivo y devuelve la lista de campos faltantes |
| Datos incompletos al marcar como ganada | No cambia el estado y devuelve la lista de campos faltantes |
| ID de oportunidad inexistente | Mensaje indicando que la oportunidad no fue encontrada |
| Backend no está corriendo | El frontend muestra `ERR_CONNECTION_REFUSED` en la consola del navegador; verificar que la Terminal 1 siga activa |
| Rutas `/frontend/...` con 404 en la terminal del frontend | Las rutas en `index.html` deben ser relativas (`style.css`, `script.js`), no absolutas con el prefijo de la carpeta |

**Datos sensibles:** la `GOOGLE_API_KEY` solo se lee vía variables de entorno; no se imprime en logs ni se incluye en respuestas. Los registros de consola de las tools muestran nombres de archivo y confirmaciones, nunca contenido de clientes ni credenciales.

---

## 11. Riesgos y limitaciones

| Riesgo | Impacto | Mitigación actual | Mejora propuesta |
|---|---|---|---|
| Ruteo no determinista del orquestador | Puede no invocar todas las tools necesarias en una consulta mixta | Reglas explícitas y ejemplos en el `SYSTEM_PROMPT` | Router determinista con LangGraph o clasificador de intención dedicado |
| Sin control de permisos por documento | Cualquier usuario ve todo el contenido | — | Metadato de rol permitido por chunk + filtro en el retriever; autenticación en la API |
| CORS abierto (`allow_origins=["*"]`) | Cualquier origen puede consumir la API | Aceptable en prototipo local | Lista blanca de dominios en producción |
| Memoria en RAM (`InMemorySaver`) | Se pierde el historial conversacional al reiniciar el backend | Botón de "nueva conversación" en el frontend para reiniciar el contexto manualmente | Checkpointer sobre base de datos persistente |
| Almacenamiento en archivos de texto plano | Sin concurrencia ni transacciones; riesgo de corrupción con escrituras simultáneas | Escritura en modo append | Migrar a una base de datos relacional |
| Sin control de costos ni de latencia | Cuota de Gemini consumible sin aviso | — | Middleware que registre tokens, latencia y errores; caché de consultas frecuentes |
| Reindexado manual | Un documento actualizado no actualiza automáticamente el índice vectorial | Documentado en este README | Watcher de la carpeta de datos o hash de contenido que dispare la reindexación |
| El cruce imagen-catálogo depende del formato exacto de extracción | Si el formato de salida de la tool multimodal varía (por ejemplo, cotizaciones con varios productos), el cruce puede no dispararse | Prompt de extracción con formato fijo por tipo de documento | Estandarizar el parseo para cubrir cotizaciones y listas de precios con múltiples productos |
| Backend y frontend deben levantarse manualmente en terminales separadas | Fácil de olvidar cuál está corriendo, especialmente tras cerrar VS Code | Documentado en la sección 6 de este README | Script único (`.bat`/`.sh`) que levante ambos procesos con un solo comando |
| Documentos ficticios de tamaño reducido | El comportamiento del RAG no está probado a mayor escala | — | Evaluación con un conjunto más amplio de preguntas y métricas de recuperación |

### Mejoras futuras

- Migrar el almacenamiento de oportunidades a una base de datos.
- Autenticación y permisos por agente y por documento.
- Panel de monitoreo: costo por consulta, latencia, tasa de "sin información suficiente", retroalimentación del usuario.
- Reindexación incremental automática ante cambios en los documentos.
- Extender el cruce del agente multimodal para cubrir cotizaciones con múltiples productos.
- Script de arranque único que levante backend y frontend con un solo comando.
- Contenerización con Docker Compose (backend, frontend y vector store).

---

## 12. Equipo

| Integrante | Componentes |
|---|---|
| Matías | Ingestión, tools de lectura, orquestador |
| Vanessa | FastAPI, Agente de acción, Agente de proceso CRM |
| Adrián Pozo | Agente multimodal, Agente de políticas, frontend |

---

## 13. Solución de problemas frecuentes

| Error | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'src'` | Se ejecutó `python archivo.py` en vez de `python -m` | Usar `python -m test.nombre_test` desde dentro de `backend/` |
| Falta `GOOGLE_API_KEY` | No existe `backend/.env` o está vacío | `copy .env.example .env` dentro de `backend/` y pegar la key |
| Los agentes responden "No encontré información suficiente" a todo | No se generaron los índices vectoriales | `python -m src.ingestion.build_indexes` desde `backend/` |
| El navegador muestra `ERR_CONNECTION_REFUSED` | El backend no está corriendo o se cerró la terminal | Verificar la Terminal 1 y volver a ejecutar `python main.py` desde `backend/` |
| El frontend carga sin estilos y no responde a ningún botón | `index.html` referencia `/frontend/style.css` y `/frontend/script.js` en vez de rutas relativas | Corregir a `href="style.css"` y `src="script.js"` |
| `404` para `style.css` o `script.js` en la terminal del frontend | Mismo problema de rutas absolutas de más | Igual que el punto anterior |
| CORS bloqueado en el navegador | Se abrió `index.html` con doble clic (`file://`) | Servir siempre con `python -m http.server 3000` desde `frontend/` |
| `TypeError: 'StructuredTool' object is not callable` | Se llamó una tool como función normal | Usar `tool.invoke({"parametro": valor})` |
| `Activate.ps1 cannot be loaded` | Política de ejecución de PowerShell | Usar `.venv\Scripts\activate.bat` |
| `cd backend` dice que la ruta no existe | La terminal está parada un nivel por encima de la carpeta real del proyecto (posible carpeta contenedora con el mismo nombre) | Verificar con `pwd` y `dir`, entrar al nivel correcto antes de `cd backend` |
