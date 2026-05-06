<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { Play, Square, CheckCircle2, Clock, Send, RefreshCw, MessageCircle, BarChart3, Trash2, History, Activity } from 'lucide-vue-next';

// ESTADO DEL SISTEMA (Inician vacíos o desconectados)
const botRunning = ref(false);
const apiStatus = reactive({ telegram: 'desconectado', whatsapp: 'desconectado' });
const queue = ref([]);
const historyList = ref([]);
const stats = reactive({ enviadosHoy: 0, pendientes: 0 });

// FUNCIONES DE CONEXIÓN CON PYTHON (API REST)
const fetchData = async () => {
  try {
    // 1. Traer estado general
    const resStatus = await fetch('/api/status');
    const dataStatus = await resStatus.json();
    botRunning.value = dataStatus.botRunning;
    apiStatus.telegram = dataStatus.apiStatus.telegram;
    apiStatus.whatsapp = dataStatus.apiStatus.whatsapp;
    stats.enviadosHoy = dataStatus.stats.enviadosHoy;
    stats.pendientes = dataStatus.stats.pendientes;

    // 2. Traer la cola de envío
    const resQueue = await fetch('/api/queue');
    queue.value = await resQueue.json();

    // 3. Traer el historial
    const resHistory = await fetch('/api/history');
    historyList.value = await resHistory.json();
    
  } catch (error) {
    console.error("Error de conexión con el motor Python:", error);
    apiStatus.telegram = 'error';
    apiStatus.whatsapp = 'error';
  }
};

// FUNCIONES DE CONTROL (Ahora envían peticiones reales a Python)
const cancelJob = async (id) => {
  console.log(`Petición para cancelar envío ID: ${id}`);
  try {
    await fetch(`/api/queue/${id}`, {
      method: 'DELETE'
    });
    // Actualización local inmediata para UX rápida (el pollInterval lo confirmará en breve)
    queue.value = queue.value.filter(item => item.id !== id);
    stats.pendientes = queue.value.length;
  } catch (error) {
    console.error("Error al cancelar el envío:", error);
  }
};

const toggleBot = async () => {
  console.log("Petición para cambiar estado del motor");
  try {
    const response = await fetch('/api/bot/toggle', {
      method: 'POST'
    });
    const data = await response.json();
    botRunning.value = data.botRunning;
  } catch (error) {
    console.error("Error al cambiar estado del bot:", error);
  }
};

// CICLO DE VIDA DEL COMPONENTE
let pollInterval;

onMounted(() => {
  // Cargar datos inmediatamente al abrir la página
  fetchData();
  
  // Refrescar los datos cada 3 segundos (Monitor en Tiempo Real)
  pollInterval = setInterval(fetchData, 3000);
});

onUnmounted(() => {
  clearInterval(pollInterval); // Limpiar memoria al cerrar
});
</script>

<template>
  <div class="min-h-screen bg-slate-50 font-sans p-6 md:p-8">
    <!-- Header (Ancho incrementado a 1600px) -->
    <div class="max-w-[1600px] mx-auto mb-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <!-- Tamaño de fuente aumentado -->
        <h1 class="text-4xl font-extrabold text-slate-800 tracking-tight flex items-center gap-4">
          <Activity class="w-10 h-10 text-indigo-600" />
          LIMS-Bridge Monitor
        </h1>
        <p class="text-slate-500 mt-2 text-lg font-medium">Panel de Envíos Multicanal (WhatsApp & Telegram)</p>
      </div>
      
      <div class="flex items-center space-x-4 bg-white p-3 rounded-2xl shadow-sm border border-slate-200">
        <div class="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-50 border border-slate-100">
          <div :class="['w-3 h-3 rounded-full', apiStatus.whatsapp === 'conectado' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500']"></div>
          <MessageCircle class="w-5 h-5 text-emerald-600" />
          <span class="text-sm font-bold text-slate-600">WhatsApp OK</span>
        </div>
        <div class="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-50 border border-slate-100">
          <div :class="['w-3 h-3 rounded-full', apiStatus.telegram === 'conectado' ? 'bg-sky-500 animate-pulse' : 'bg-red-500']"></div>
          <Send class="w-5 h-5 text-sky-600" />
          <span class="text-sm font-bold text-slate-600">Telegram OK</span>
        </div>
      </div>
    </div>

    <!-- Contenedor Principal (Ancho incrementado a 1600px) -->
    <div class="max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-10">
      
      <!-- COLUMNA IZQUIERDA: CONTROLES -->
      <div class="lg:col-span-4 space-y-8">
        
        <div class="bg-white rounded-3xl shadow-sm border border-slate-200 p-10 text-center relative overflow-hidden">
          <div v-if="botRunning" class="absolute inset-0 bg-indigo-50/50 -z-10 animate-pulse"></div>
          <div class="mb-8 relative z-10">
            <div :class="['inline-flex items-center justify-center w-28 h-28 rounded-full mb-6 transition-all duration-500', botRunning ? 'bg-indigo-100 text-indigo-600 scale-110 shadow-inner' : 'bg-slate-100 text-slate-400']">
              <RefreshCw v-if="botRunning" class="w-14 h-14 animate-spin" />
              <Send v-else class="w-14 h-14" />
            </div>
            <h2 class="text-2xl font-bold text-slate-800">{{ botRunning ? 'Despachando...' : 'Motor Detenido' }}</h2>
          </div>
          
          <button 
            @click="toggleBot" 
            :disabled="queue.length === 0 && !botRunning" 
            :class="['w-full py-5 px-6 rounded-2xl font-bold text-xl flex items-center justify-center space-x-3 transition-all shadow-md relative z-10', botRunning ? 'bg-rose-500 hover:bg-rose-600 text-white shadow-rose-200' : (queue.length === 0 ? 'bg-slate-200 text-slate-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-200')]"
          >
            <template v-if="botRunning">
              <Square class="w-6 h-6 fill-current" /> <span>Detener Motor</span>
            </template>
            <template v-else>
              <Play class="w-6 h-6 fill-current" /> <span>Iniciar Motor</span>
            </template>
          </button>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
            <div class="flex items-center space-x-2 text-indigo-600 mb-3">
              <CheckCircle2 class="w-6 h-6" /> 
              <span class="font-bold text-base">Enviados</span>
            </div>
            <!-- Tamaño de números aumentado -->
            <span class="text-5xl font-black text-slate-800">{{ stats.enviadosHoy }}</span>
          </div>
          <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
            <div class="flex items-center space-x-2 text-amber-500 mb-3">
              <Clock class="w-6 h-6" /> 
              <span class="font-bold text-base">En Cola</span>
            </div>
            <!-- Tamaño de números aumentado -->
            <span class="text-5xl font-black text-slate-800">{{ stats.pendientes }}</span>
          </div>
        </div>

        <button class="w-full py-5 px-6 rounded-2xl font-bold text-lg text-slate-700 bg-white border border-slate-200 hover:bg-indigo-50 hover:border-indigo-200 hover:text-indigo-700 transition-all shadow-sm flex items-center justify-center space-x-3 group">
          <BarChart3 class="w-6 h-6 text-slate-400 group-hover:text-indigo-600" />
          <span>Ver Analíticas e Historial</span>
        </button>
      </div>

      <!-- COLUMNA DERECHA: LISTAS -->
      <!-- Altura configurada para ocupar la pantalla dinámica (calc) con un mínimo -->
      <div class="lg:col-span-8 bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden flex flex-col h-[calc(100vh-180px)] min-h-[700px]">
        
        <div class="flex border-b border-slate-100">
          <div class="px-8 py-5 border-b-2 border-indigo-600 bg-indigo-50/30 flex items-center space-x-3 flex-1">
            <Clock class="w-5 h-5 text-indigo-600" />
            <span class="font-bold text-lg text-indigo-900">Cola de Envío ({{ queue.length }})</span>
          </div>
          <div class="px-8 py-5 flex items-center space-x-3 opacity-60 bg-slate-50 flex-1 border-l border-slate-100">
            <History class="w-5 h-5 text-slate-500" />
            <span class="font-bold text-lg text-slate-600">Historial Reciente</span>
          </div>
        </div>

        <div class="flex-1 overflow-auto p-8 bg-slate-50/50">
          
          <!-- Lista de Cola -->
          <div class="mb-10">
            <div v-if="queue.length === 0" class="text-center py-12 bg-white rounded-2xl border border-slate-200 border-dashed">
              <CheckCircle2 class="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <p class="text-slate-500 text-lg font-medium">No hay estudios pendientes en la cola.</p>
            </div>
            <ul v-else class="space-y-4">
              <li v-for="(item, index) in queue" :key="item.id" :class="['bg-white border rounded-2xl p-5 flex items-center justify-between shadow-sm transition-all hover:shadow-md', botRunning && index === 0 ? 'border-indigo-300 shadow-indigo-100/50 ring-2 ring-indigo-50' : 'border-slate-200']">
                <div class="flex items-center space-x-5">
                  <div :class="['w-12 h-12 rounded-full flex items-center justify-center font-bold text-base', index === 0 && botRunning ? 'bg-indigo-100 text-indigo-600 animate-pulse' : 'bg-slate-100 text-slate-600']">
                    <RefreshCw v-if="botRunning && index === 0" class="w-5 h-5 animate-spin" />
                    <span v-else>{{ index + 1 }}</span>
                  </div>
                  <div>
                    <p class="font-bold text-lg text-slate-800 flex items-center gap-2">Muestra #{{ item.id }}</p>
                    <p class="text-base text-slate-500">{{ item.paciente }}</p>
                    
                    <!-- Etiquetas multicanal -->
                    <div class="flex space-x-2 mt-2">
                      <span v-if="item.channels.includes('whatsapp')" class="inline-flex items-center space-x-1 bg-emerald-50 text-emerald-600 px-2.5 py-1 rounded-md text-[11px] font-bold border border-emerald-100">
                        <MessageCircle class="w-3.5 h-3.5" /> <span>WA</span>
                      </span>
                      <span v-if="item.channels.includes('telegram')" class="inline-flex items-center space-x-1 bg-sky-50 text-sky-600 px-2.5 py-1 rounded-md text-[11px] font-bold border border-sky-100">
                        <Send class="w-3.5 h-3.5" /> <span>TG</span>
                      </span>
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-5">
                  <div class="flex flex-col items-end">
                    <span class="text-sm font-medium text-slate-400 mb-1.5">{{ item.time }}</span>
                    <span :class="['px-3.5 py-1.5 rounded-full text-xs font-bold', botRunning && index === 0 ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500']">
                      {{ botRunning && index === 0 ? 'Enviando...' : 'En Espera' }}
                    </span>
                  </div>
                  <button 
                    v-if="!(botRunning && index === 0)"
                    @click="cancelJob(item.id)"
                    class="p-2.5 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-xl transition-colors"
                    title="Cancelar envío"
                  >
                    <Trash2 class="w-6 h-6" />
                  </button>
                </div>
              </li>
            </ul>
          </div>

          <!-- Lista de Historial -->
          <div>
            <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-5 px-2 flex items-center gap-2">
              <CheckCircle2 class="w-5 h-5" /> Ya despachados
            </h3>
            <ul class="space-y-4">
              <li v-for="item in historyList" :key="item.id" class="bg-white/80 border border-slate-200/60 rounded-2xl p-5 flex items-center justify-between opacity-80 hover:opacity-100 transition-opacity">
                <div class="flex items-center space-x-5">
                  <div class="w-12 h-12 rounded-full bg-slate-50 border border-slate-100 text-emerald-500 flex items-center justify-center">
                    <CheckCircle2 class="w-6 h-6" />
                  </div>
                  <div>
                    <p class="font-bold text-lg text-slate-700 line-through decoration-slate-300">Muestra #{{ item.id }}</p>
                    <p class="text-base text-slate-500">{{ item.paciente }}</p>
                    <div class="flex space-x-2 mt-2">
                      <span v-if="item.channels.includes('whatsapp')" class="inline-flex items-center space-x-1 bg-emerald-50 text-emerald-600 px-2.5 py-1 rounded-md text-[11px] font-bold border border-emerald-100">
                        <MessageCircle class="w-3.5 h-3.5" /> <span>WA</span>
                      </span>
                      <span v-if="item.channels.includes('telegram')" class="inline-flex items-center space-x-1 bg-sky-50 text-sky-600 px-2.5 py-1 rounded-md text-[11px] font-bold border border-sky-100">
                        <Send class="w-3.5 h-3.5" /> <span>TG</span>
                      </span>
                    </div>
                  </div>
                </div>
                <div class="flex flex-col items-end">
                  <span class="text-sm font-medium text-slate-400 mb-1.5">{{ item.time }}</span>
                  <span class="text-sm font-bold text-emerald-600">Entregado</span>
                </div>
              </li>
            </ul>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>
