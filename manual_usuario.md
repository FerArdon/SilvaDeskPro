# SilvaDesk Pro — Manual Oficial de Usuario
## Sistema de Gestión Forestal Profesional
*Honduras · Versión 1.0,0*

![SilvaDesk Pro Banner](file:///C:/Users/frard/.gemini/antigravity/brain/34117303-e826-4129-870b-5538e4bdc63c/manual_banner_1781567233950.png)

---

## Introducción a SilvaDesk Pro

**SilvaDesk Pro** es un entorno de software especializado diseñado para ingenieros forestales en Honduras. Combina el control operativo del **Protocolo de Actuaciones Técnicas** (Bitácora) con las herramientas administrativas y legales del **Facturador Forestal (conforme SAR)** y la **Calculadora de Aranceles COLPROFORH (La Gaceta No. 36,609, 10/08/2024)**.

El sistema se rige bajo principios de rigor documental y trazabilidad legal, permitiendo al profesional actuar en calidad de ministro de fe y administrar sus servicios técnicos con absoluta precisión operativa.

---

## 1.📓 Bitácora de Actuaciones Técnicas

La Bitácora es el corazón jurídico de SilvaDesk Pro. Permite a los peritos forestales registrar y dar seguimiento a las inspecciones, avalúos y peritajes en el marco del **Protocolo de Actuaciones Técnicas**, generando documentos PDF formales y foliados con valor legal pleno.

![Bitácora de Actuaciones Técnicas](file:///C:/Users/frard/.gemini/antigravity/brain/34117303-e826-4129-870b-5538e4bdc63c/bitacora_icon_1781567249230.png)

### 1.1. Barra de Herramientas Operativa
Ubicada en la parte superior de la pestaña, provee control directo sobre los registros de actas:

*   **📜 Nueva Acta**: Abre el formulario completo para asentar una nueva diligencia en el protocolo.
*   **✏️ Editar**: Permite modificar la información del acta seleccionada en la tabla (bloqueada para actas anuladas).
*   **📄 Ver / Imprimir**: Genera y exporta en tiempo real un PDF del acta en formato notarial bajo la estructura del Ministerio Público y la Sección Técnica Ambiental. Si la generación es exitosa, ofrece la opción de visualizar el PDF de inmediato.
*   **🗑 Anular**: En consonancia con el principio de protocolo jurídico, las actas no se borran físicamente del sistema, sino que se marcan en la base de datos como **"Anulada"** y su visualización en el PDF cambia para dejar registro del estado.
*   **Filtro "Estado"**: Un menú desplegable (`Combobox`) que permite refinar los registros visibles en la tabla de acuerdo a su estado de trámite: *Todos, Activa, En trámite, Elevada a proceso penal, Archivada y Anulada*.
*   **🔍 Entrada de Búsqueda**: Cuadro de búsqueda dinámica. Permite filtrar los registros en tiempo real al escribir el número de acta, número de expediente FEMA, tipo de diligencia, lugar de los hechos, nombres de comparecientes o detalles del hecho constatado.

### 1.2. Tabla de Protocolo (Treeview)
Muestra un resumen de todos los registros del protocolo ordenados descendentemente por su número de **Folio**. Cuenta con una coloración inteligente para identificar de inmediato el estado del expediente:
*   🟢 **Verde Claro (Activa)**: Actas en vigencia.
*   🟡 **Amarillo (En trámite)**: Diligencia técnica en desarrollo o a la espera de resolución administrativa.
*   🔴 **Rosa (Elevada a proceso penal)**: Casos judicializados remitidos a la Fiscalía de Medio Ambiente (FEMA) o juzgados de la República.
*   ⚪ **Gris Claro (Archivada)**: Procesos concluidos.
*   ⚫ **Gris Opaco / Tachado (Anulada)**: Actas que perdieron validez pero permanecen para efectos de trazabilidad legal.

### 1.3. Diálogo de Nueva / Editar Acta
El formulario de ingreso está estructurado en cinco bloques lógicos que guían al profesional para no omitir ningún dato de relevancia jurídica:

#### Sección 1: Identificación del Acta
*   **Acta No. (\*)**: Código identificador único del acta (Generado automáticamente correlacionando el año actual, por ejemplo: `001-2026`).
*   **Folio**: Número consecutivo de página correspondiente al libro del protocolo (calculado automáticamente sumando 1 al máximo folio existente en la base de datos).
*   **Tipo de Diligencia (\*)**: Selector con los 14 tipos principales definidos por la práctica institucional y el arancel (ej. *Inspección Ocular, Dictamen Técnico Pericial, Acta de Decomiso, Finiquito Regla 3x1*).
*   **Expediente FEMA No.**: Código del expediente en la Fiscalía Especial de Medio Ambiente que origina la orden técnica.

#### Sección 2: Lugar y Tiempo
*   **Fecha (\*)**: Fecha de la actuación de campo en formato `DD/MM/AAAA` (por defecto se coloca la fecha actual del sistema).
*   **Hora (\*)**: Hora del inicio de la actuación en formato de 24 horas (`HH:MM`).
*   **Lugar / Sitio**: Dirección física, predio o coordenadas del lugar inspeccionado.
*   **Municipio**: Nombre de la demarcación territorial.
*   **Departamento**: Selector con los 18 departamentos de la República de Honduras (por defecto *Francisco Morazán*).

#### Sección 3: Comparecientes y Presentes
*   **Personas presentes (\*)**: Campo de texto enriquecido multi-línea. Se debe registrar un compareciente por línea, indicando su nombre completo, cargo o institución que representa, y número de tarjeta de identidad (DNI).

#### Sección 4: Contenido Técnico
*   **Hechos constatados (\*)**: Narrativa fáctica y objetiva de lo observado en campo por el perito, incluyendo daños ambientales, aprovechamientos forestales, afectaciones o alteraciones de recursos.
*   **Hallazgos técnicos (\*)**: Conclusiones e interpretaciones profesionales de los hechos (ej. cubicación del volumen de madera afectada, identificación de especies forestales, estimación del área desmontada o tasas de regeneración natural).

#### Sección 5: Fundamento Legal y Disposición
*   **Fundamento legal**: Selector rápido con las leyes aplicables al sector forestal hondureño (ej. *Art. 100 LFAPVS - Aprovechamiento ilegal, Art. 103 - Daño a ecosistemas, Art. 172 Código Penal - Daños al medio ambiente, PCM-002-2006 - Incumplimiento Regla 3x1, o redacción libre*).
*   **Disposición / Recomendación**: Medidas recomendadas al órgano judicial o administrativo con base en el hallazgo (decomisos, paralizaciones, o inicio de reforestación obligatoria).
*   **Estado del acta**: Selector del estado del trámite en curso (*Activa, En trámite, Elevada a proceso penal, Archivada, Anulada*).
*   **Observaciones**: Cualquier acotación técnica adicional relevante.

*Los campos marcados con asterisco (\*) son de llenado obligatorio para asegurar la validez formal del acta.*

---

## 2.🧾 Facturador Forestal (SAR)

El Facturador automatiza el cálculo de impuestos y honorarios profesionales con estricto cumplimiento del régimen de facturación de la **Servicio de Administración de Rentas (SAR)** de Honduras.

![Facturador Forestal](file:///C:/Users/frard/.gemini/antigravity/brain/34117303-e826-4129-870b-5538e4bdc63c/facturador_icon_1781567262207.png)

La interfaz se divide en dos paneles funcionales mediante un divisor deslizable (`PanedWindow`): el **Formulario de Emisión** a la izquierda, y el **Historial de Facturas** a la derecha.

### 2.1. Panel de Emisión de Facturas (Izquierdo)

#### Bloque SAR - CAI (Obligatorio)
Este bloque contiene los datos fiscales de control requeridos por las leyes de Honduras:
*   **CAI**: Código de Autorización de Impresión otorgado por la SAR. Se ingresa en formato estándar de 32 caracteres.
*   **Fecha Límite Emisión**: Fecha límite permitida para emitir documentos bajo la autorización del CAI (`DD/MM/AAAA`).
*   **Rango Inicio / Rango Fin**: Rango de numeración autorizado para la emisión de facturas (ej. `000-001-01-00000001` al `000-001-01-00000500`).

#### Bloque 1: Datos del Emisor
Campos del profesional que expide el recibo o la empresa consultora. Se auto-completan dinámicamente según la configuración activa de la licencia (nombre, RTN, dirección y teléfono).

#### Bloque 2: Datos del Cliente
*   **Nombre / Razón Social**: Persona o entidad a quien se le factura el servicio.
*   **RTN Cliente**: Registro Tributario Nacional del obligado tributario (14 dígitos).
*   **Dirección**: Domicilio fiscal del cliente.

#### Bloque 3: Fecha
*   **Fecha de Emisión**: Fecha de corte fiscal de la factura (inicializada con la fecha actual en formato `DD/MM/AAAA`).

#### Bloque 4: Servicios a Facturar
Permite cargar de forma estructurada e ilimitada los ítems a cobrar:
1.  **Selector de Servicio**: Menú que expone los servicios arancelarios predefinidos de COLPROFORH (ej. *POA, PMF, Peritajes, Desarrollo de Software, Regencias, etc.*) con sus precios de referencia.
2.  **Entrada Cantidad**: Cantidad de unidades físicas del servicio (por ejemplo: m³, horas, hectáreas, o número de memorias técnicas). Admite decimales.
3.  **Entrada Precio Unitario**: Precio de tarifa en Lempiras (L.). Puede editarse libremente para fijar precios especiales o personalizados.
4.  **Botón ➕ Agregar**: Incorpora el servicio y la cantidad a la tabla intermedia de ítems facturados.
5.  **Tabla de ítems**: Detalla el listado actual de conceptos cargados para la factura con sus totales individuales.
6.  **Botón 🗑 Quitar Seleccionado**: Elimina un ítem específico seleccionado en la lista, recalculando automáticamente el total de la factura.

#### Bloque 5: Desglose de Totales (Live)
Muestra la estimación de cobro en tiempo real:
*   **Subtotal**: Sumatoria de todos los servicios agregados (Honorario base).
*   **ISV (15%)**: Impuesto sobre Ventas del 15% que debe cobrarse al cliente y ser declarado mensualmente ante el SAR.
*   **TOTAL FACTURA**: Total oficial facturado (Subtotal + ISV 15%). Corresponde al monto legal que se registra en la factura.
*   **ISR (12.5%)\***: Impuesto sobre la Renta referencial (retenido por el cliente en caso de que sea persona jurídica, de acuerdo con el Art. 50 de la Ley de ISR de Honduras).
*   **Neto a Cobrar\***: Estimación del valor líquido final que el profesional recibirá tras la aplicación de la retención del cliente.

*\*El cálculo del ISR de retención se muestra únicamente a modo informativo y referencial para el profesional forestal. Por disposición legal (Ley del Impuesto sobre la Renta), no se carga en el total de la factura, dado que es el cliente quien retiene y entera el impuesto ante el SAR.*

#### Bloque 6: Observaciones y Emisión
*   **Observaciones**: Espacio libre para registrar métodos de pago, número de cuenta bancaria o condicionamientos del servicio.
*   **Botón 💾 EMITIR FACTURA (Guardar + PDF)**: Guarda la factura en la base de datos local y genera el archivo PDF correspondiente en el directorio `Facturas/` con el membrete oficial, marca de agua e información de cumplimiento fiscal.

---

### 2.2. Panel de Historial de Facturas (Derecho)

Actúa como una copia en el sistema de todas las facturas emitidas, permitiendo auditar y dar trazabilidad fiscal:

*   **Filtros de Visualización**: Botones de opción rápida para segmentar las facturas: *Todas, ✅ Activas (vigentes) y ⛔ Anuladas*.
*   **Filtro por Entrada**: Entrada dinámica que busca registros coincidentes con el número de factura, fecha de emisión o nombre del cliente.
*   **Tabla de Historial**: Lista ordenada descendentemente que muestra el identificador de factura, fecha, cliente, monto total y estado. Las facturas anuladas se muestran visualmente de forma diferenciada (en texto color rojo tenue y tachado) para evitar confusiones de cobro.
*   **Botón 📄 Abrir PDF**: Abre de forma inmediata el archivo PDF de la factura seleccionada en el lector predeterminado del sistema operativo.
*   **Botón ✏️ Editar**: Carga toda la información, CAI, cliente y lista de servicios de la factura seleccionada de vuelta en el formulario izquierdo para realizar modificaciones de manera rápida, actualizando el PDF y la base de datos al presionar el botón de confirmación. *(Esta opción está inhabilitada para facturas anuladas)*.
*   **Botón ⛔ Anular**: Inicia el protocolo de anulación de facturas:
    1.  Abre un diálogo obligatorio para que el usuario registre la justificación técnica de la anulación.
    2.  Actualiza el estado de la factura a **"ANULADA"** en la base de datos de manera permanente.
    3.  Regenera el archivo PDF de la factura aplicando una **marca de agua cruzada** y leyendas con la palabra "ANULADA" en color rojo translúcido, manteniendo así la validez del registro fiscal SAR pero impidiendo su cobro.
*   **Botón 🔄 Actualizar**: Vuelve a cargar y refrescar los registros de la base de datos en la tabla.

---

## 3.🌿 Calculadora de Aranceles COLPROFORH

Esta pestaña funciona como un simulador financiero de los honorarios mínimos permitidos para el ejercicio de la profesión, basándose estrictamente en el **Arancel de Servicios Profesionales de COLPROFORH (La Gaceta No. 36,609)**.

![Calculadora de Aranceles](file:///C:/Users/frard/.gemini/antigravity/brain/34117303-e826-4129-870b-5538e4bdc63c/calculadora_icon_1781567276352.png)

La calculadora consta de **8 bloques independientes** organizados en dos columnas que actualizan de forma instantánea todos los rubros arancelarios al modificar los parámetros amarillos de entrada. Cada bloque realiza el desglose automático de: **Honorario Base**, **ISV (15%)**, **Total a Facturar**, **ISR de Retención (12.5%)** y **Neto a Recibir**.

### 3.1. Detalle de los 8 Bloques de Cálculo

#### Bloque 1: Consultoría por Hora (Ingeniero Universitario - Categoría C)
Diseñado para la asistencia técnica directa, auditorías rápidas o asesoramientos:
*   **Entradas**:
    *   *Tarifa base / hora (L.)*: Inicializado en **L. 722.66** (Tarifa arancelaria vigente para Ingeniero Categoría C).
    *   *Número de horas*: Cantidad de horas estimadas (el sistema advierte un mínimo de 2 horas según el Art. 9 del Arancel).
    *   *Movilización (L.)*: Costo base por transporte o viáticos del consultor.
*   **Fórmula del Honorario Base**:
    $$\text{Honorario Base} = (\text{Tarifa hora} \times \text{Horas}) + \text{Movilización}$$

#### Bloque 2: Plan de Manejo Forestal (PMF)
Calcula el costo del levantamiento de inventarios y redacción del plan para un bosque completo:
*   **Entradas**:
    *   *Volumen del plan (m³)*: Volumen total comercial estimado.
    *   *¿Propiedad > 100 ha?*: Selección binaria (*Sí / No*). Si la propiedad es menor a 100 hectáreas, la tarifa mínima es de **L. 120.00** por m³. Si es mayor a 100 hectáreas, se aplica una tasa de **L. 80.00** por m³.
*   **Fórmula del Honorario Base**:
    $$\text{Honorario Base} = \text{Volumen (m³)} \times \text{Tarifa por superficie}$$

#### Bloque 3: Plan Operativo Anual (POA)
Fija los montos por la delimitación de parcelas de corta anuales:
*   **Entradas**:
    *   *Volumen del POA (m³)*: Volumen de extracción autorizado.
    *   *Servicio*: Tres modalidades:
        1.  *Elaboración del plan*: Tarifa de **L. 150.00** por m³.
        2.  *Administración de la corta*: Tarifa de **L. 120.00** por m³.
        3.  *Ambos (Elaboración + Administración)*: Tarifa combinada de **L. 270.00** por m³.
*   **Fórmula del Honorario Base**:
    $$\text{Honorario Base} = \text{Volumen (m³)} \times \text{Tarifa del servicio seleccionado}$$

#### Bloque 4: Peritaje Judicial / Civil o Administrativo
Calcula los honorarios del perito asignado a demandas civiles, arbitrajes de propiedad o reclamos ante seguros:
*   **Entradas**:
    *   *Valor de la demanda (L.)*: Cuantía económica exigida en el juicio.
*   **Fórmula del Honorario Base** (Art. 12 del Arancel):
    $$\text{Honorario Base} = \text{Valor de la demanda} \times 15\% \ (0.15)$$
*   *Nota: Este bloque incluye una advertencia especial aclarando que solo aplica para procesos civiles o administrativos. No aplica para procesos penales.*

#### Bloque 5: Finiquito - Regla 3×1 (PCM-002-2006)
Calcula la certificación técnica del cumplimiento de reforestación obligatoria (compensación de 3 árboles plantados por cada 1 aprovechado):
*   **Entradas**:
    *   *Superficie de la propiedad (ha)*: Tamaño catastral del predio forestal.
*   **Fórmula de Tarifa Plana**:
    *   Si la superficie es menor a 100 hectáreas: **L. 30,000.00**.
    *   Si la superficie es igual o mayor a 100 hectáreas: **L. 50,000.00**.

#### Bloque 6: Establecimiento / Certificación de Plantaciones
Fija los montos de cobro para el registro oficial de plantaciones forestales comerciales:
*   **Entradas**:
    *   *Hectáreas*: Cantidad de tierra plantada.
    *   *Servicio*: Dos opciones:
        1.  *Establecimiento*: Cobro de **L. 10,000.00** por hectárea.
        2.  *Certificación*: Cobro base de **L. 5,000.00** para las primeras 10 hectáreas, más **L. 2,000.00** por cada hectárea adicional.
*   **Fórmulas**:
    *   *Establecimiento*:
        $$\text{Honorario Base} = \text{Hectáreas} \times 10,000.00$$
    *   *Certificación*:
        $$\text{Honorario Base} = (\min(\text{Hectáreas}, 10) \times 5,000.00) + (\max(0, \text{Hectáreas} - 10) \times 2,000.00)$$

#### Bloque 7: Peritaje en Proceso Penal (CPP Art. 124)
Fórmula especial aplicada a peritajes ordenados por el Ministerio Público (FEMA) o tribunales penales por delitos ambientales. A diferencia del bloque civil, no existe un "monto demandado":
*   **Entradas**:
    *   *Horas invertidas*: Tiempo en campo, gabinete y redacción del dictamen técnico.
    *   *Tarifa horaria*: Inicializado en **L. 722.66** (Categoría C).
    *   *Volumen ilegal (m³)*: Volumen del producto forestal decomisado u objeto de delito (si aplica).
    *   *Tarifa avalúo (L./m³)*: Tarifa arancelaria de avalúo forestal fijada en **L. 300.00** por m³.
    *   *Movilización / Viáticos (L.)*: Gastos operativos de transporte del perito.
*   **Fórmula del Honorario Base**:
    $$\text{Honorario Base} = (\text{Horas} \times \text{Tarifa horaria}) + (\text{Volumen ilegal} \times 300.00) + \text{Movilización}$$

#### Bloque 8: Software Forestal / Ambiental Especializado
Bloque exclusivo incorporado para la estimación de honorarios en el desarrollo de herramientas tecnológicas de ingeniería forestal (ej. *sistemas de información geográfica personalizados, gestores de expedientes o licencias como SilvaDesk Pro*):
*   **Entradas**:
    *   *Tarifa hora desarrollo (L.)*: Tarifa de programación e ingeniería de software (inicializada en **L. 1,500.00** por hora).
    *   *Horas de desarrollo*: Estimación del tiempo dedicado a diseño, codificación, depuración e implantación del sistema.
    *   *Módulos adicionales (cant.)*: Número de componentes o integraciones complejas (ej. módulo de mapas SIG, facturador SAR, gestor de firmas).
    *   *Precio por módulo (L.)*: Precio de licenciamiento de cada módulo funcional (inicializado en **L. 8,000.00**).
    *   *Licencia perpetua (L.)*: Valor de licenciamiento comercial del software base (inicializado en **L. 20,000.00**).
    *   *Movilización / Viáticos (L.)*: Gastos operativos del ingeniero de sistemas/forestal.
    *   *% Mantenimiento anual*: Porcentaje cobrado por soporte y actualizaciones del sistema (inicializado en **15%** anual).
*   **Cálculos**:
    *   **Honorario Base (Desarrollo inicial)**:
        $$\text{Honorario Base} = (\text{Tarifa hora} \times \text{Horas}) + (\text{Módulos} \times \text{Precio módulo}) + \text{Licencia perpetua} + \text{Movilización}$$
    *   **Mantenimiento Anual (Referencial para contrato subsiguiente)**:
        $$\text{Mantenimiento Anual} = \text{Honorario Base} \times \left(\frac{\text{Porcentaje Mantenimiento}}{100}\right)$$

---

## 4.ℹ️ Acerca de y Configuración Dinámica de Licencia

Esta sección centraliza el control de identidad institucional del software, permitiendo adaptar los datos de emisión a otros profesionales forestales o consultoras de manera rápida.

```
       [ Pestaña "Acerca de" ] ──⚙️ Botón Configurar Licencia
                 │
                 ├── Nombre de Empresa / Institución (SEDCAF / FEMA)
                 ├── Nombre Completo del Profesional Emisor
                 ├── Registro Profesional (COLPROFORH N.° 0226)
                 ├── RTN del Emisor
                 ├── Dirección Comercial
                 └── Teléfono de Contacto
```

Al pulsar el botón **"⚙️ Configurar Empresa / Licencia"**, se despliega un formulario que permite actualizar de forma persistente los datos en la base de datos `SilvaDesk.db`.

### 4.1. Impacto en Caliente de la Configuración:
*   **En la cabecera (Header) del programa**: Cambia los datos del emisor y el número de colegiado COLPROFORH expuestos de forma permanente en la parte superior.
*   **En el Facturador**: Al emitir una factura, los datos fiscales del emisor (Nombre, RTN, dirección, teléfono) se auto-completan con los nuevos valores ingresados en la configuración.
*   **En la Bitácora (Firmas)**: Al generar el PDF notarial de un acta de la bitácora, el bloque de firma de pie de página se actualiza automáticamente con el nombre del nuevo profesional consultor y la institución.
