#include <esp_now.h>
#include <WiFi.h>
#include <esp_wifi.h>

#define ID_MINHA_EQUIPE 2026

//Endereço MAC de Broadcast
uint8_t mac_broadcast[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

typedef struct mensagem_mlt3 {
  uint16_t id_grupo;
  int8_t niveis[150];
  int tamanho;
} mensagem_mlt3;

mensagem_mlt3 pacote_envio;
mensagem_mlt3 pacote_recebido;

// função RX: Recebe e manda pro Python 

void aoReceberDados(const uint8_t * mac, const uint8_t *dadosRecebidos, int len) {
  memcpy(&pacote_recebido, dadosRecebidos, sizeof(pacote_recebido));

  if (pacote_recebido.id_grupo != ID_MINHA_EQUIPE) {
    return; 
  }
  
  // envia com o prefixo "RX:" para o Python saber que é uma mensagem
  Serial.print("RX:"); 
  
  for (int i = 0; i < pacote_recebido.tamanho; i++) {
    Serial.print(pacote_recebido.niveis[i]);
    if (i < pacote_recebido.tamanho - 1) {
      Serial.print(","); // Adiciona vírgulas, menos no último número
    }
  }
  Serial.println(); // Envia quebra de linha avisando o Python que terminou
}

// SETUP: Configurações de Rede e Rádio
void setup() {
  Serial.begin(115200); // Mesma velocidade configurada no Python
  
  // Liga o Wi-Fi no modo Station (Padrão)
  WiFi.mode(WIFI_STA);
  
  // 
  // AJUSTE DE FREQUÊNCIA: Força o ESP32 a ficar no Canal 1
  // Garante que o Host A e o Host B sempre se encontrem no rádio
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);
  esp_wifi_set_promiscuous(false);
  
  // Inicializa o protocolo ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Erro ao inicializar ESP-NOW");
    return;
  }
  
  // Registra a função de escuta (quando chegar dados pelo rádio, roda a função)
  esp_now_register_recv_cb(esp_now_recv_cb_t(aoReceberDados));

  // Configura a quem vamos enviar as mensagens (Neste caso: Broadcast / Todos)
  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, mac_broadcast, 6);
  peerInfo.channel = 1;  // <-- AJUSTADO: Fixo no Canal 1 para casar com o rádio
  peerInfo.encrypt = false;
  
  // Adiciona o endereço de Broadcast à lista de permissões
  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Erro ao registrar o Broadcast");
    return;
  }
}

// LOOP (TX): Ouve o Python (Cabo USB) e manda pro ar (ESP-NOW)
void loop() {
  if (Serial.available()) {
    // Lê a mensagem do Python até ele dar um (\n)
    String recebido_do_pc = Serial.readStringUntil('\n'); 
    recebido_do_pc.trim();
    
    if (recebido_do_pc.length() > 0) {

      pacote_envio.id_grupo = ID_MINHA_EQUIPE;
      char buffer[500]; 
      recebido_do_pc.toCharArray(buffer, sizeof(buffer));
      
      // Quebra a string nas vírgulas
      char* token = strtok(buffer, ",");
      int indice = 0;
      
      // Converte cada fatia de texto em número e salva no pacote
      while (token != NULL && indice < 150) {
        pacote_envio.niveis[indice] = atoi(token); 
        indice++;
        token = strtok(NULL, ","); 
      }
      
      pacote_envio.tamanho = indice;
      
      esp_now_send(mac_broadcast, (uint8_t *) &pacote_envio, sizeof(pacote_envio));
    }
  }
}
