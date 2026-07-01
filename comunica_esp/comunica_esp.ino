//Feito com auxilio do Google Gemini
#include <esp_now.h>
#include <WiFi.h>
#include <esp_wifi.h>

#define ID_MINHA_EQUIPE 2026

//Endereço MAC de Broadcast
uint8_t mac_broadcast[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

typedef struct mensagem_mlt3 {
  uint16_t id_grupo;
  char esp_origem[10];
  int8_t niveis[200];
  int tamanho;
} mensagem_mlt3;

mensagem_mlt3 pacote_envio;
mensagem_mlt3 pacote_recebido;

// LOOP: ESP32 para Python

void aoReceberDados(const uint8_t * mac, const uint8_t *dadosRecebidos, int len) {
  memcpy(&pacote_recebido, dadosRecebidos, sizeof(pacote_recebido));

  if (pacote_recebido.id_grupo != ID_MINHA_EQUIPE) {
    return; 
  }
  
  Serial.print("RX:"); 
  Serial.print(pacote_recebido.esp_origem);
  Serial.print(":");
  
  for (int i = 0; i < pacote_recebido.tamanho; i++) {
    Serial.print(pacote_recebido.niveis[i]);
    if (i < pacote_recebido.tamanho - 1) {
      Serial.print(","); 
    }
  }
  Serial.println(); 
}

// SETUP: Configurações do ESP-NOW
void setup() {
  Serial.begin(115200); 
  
  WiFi.mode(WIFI_STA);
  
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);
  esp_wifi_set_promiscuous(false);
  
  // Inicializa o protocolo ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Erro ao inicializar ESP-NOW");
    return;
  }
  
  esp_now_register_recv_cb(esp_now_recv_cb_t(aoReceberDados));

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, mac_broadcast, 6);
  peerInfo.channel = 1;  
  peerInfo.encrypt = false;
  
  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Erro ao registrar o Broadcast");
    return;
  }
}

// LOOP: Python Para o ESP32
void loop() {
  if (Serial.available()) {
    // Lê a mensagem do Python até ele dar um (\n)
    String recebido_do_pc = Serial.readStringUntil('\n'); 
    recebido_do_pc.trim();
    
    if (recebido_do_pc.length() > 0) {

      pacote_envio.id_grupo = ID_MINHA_EQUIPE;
      
      int pos_dois_pontos = recebido_do_pc.indexOf(':');
      String id_remetente = "Desconhecido";
      String dados_niveis = recebido_do_pc;

      if (pos_dois_pontos != -1) {
        id_remetente = recebido_do_pc.substring(0, pos_dois_pontos);
        dados_niveis = recebido_do_pc.substring(pos_dois_pontos + 1);
      }

      strncpy(pacote_envio.esp_origem, id_remetente.c_str(), sizeof(pacote_envio.esp_origem));

      char buffer[1000]; 
      dados_niveis.toCharArray(buffer, sizeof(buffer)); 

      
      char* token = strtok(buffer, ",");
      int indice = 0;
      
      while (token != NULL && indice < 200) {
        pacote_envio.niveis[indice] = atoi(token); 
        indice++;
        token = strtok(NULL, ","); 
      }
      
      pacote_envio.tamanho = indice;
      
      esp_now_send(mac_broadcast, (uint8_t *) &pacote_envio, sizeof(pacote_envio));
    }
  }
}
