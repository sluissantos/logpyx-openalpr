
# LOGPYX PLATE RECOGNIZER
> Este documento detalha os passos necessários para rodar a rotina de processamento principal (Main processing) do Logpyx Plate Recognizer utilizando o seu respectivo container docker.

## 💻 Pré-Requisitos

Antes de começar, verifique se você atendeu aos seguintes requisitos:
* Materiais necessários:
	* Câmera IP conectada à rede.
	* Definição das variáveis de ambiente no sistema a ser rodada a aplicação. Será detalhado posteriormente.
* Ter instalado as dependências listadas no arquivo `instal.sh` casoa aplicação seja rodada em uma máquina.
* Ter instalado algum container de identificação de carga:
	* RFID (jeadias/logpyx_warehouse_rfid) - opcional. ²
	* Código de barras com Câmera (a ser feito) - opcional.


### Download do executável principal e do arquivo de configurações
Antes de instalar os containers, é necessário criar a pasta `app` no diretório `/home/torizon`, caso já não tenha sido criada, para receber os binários de processamento e os arquivos de configuração:
Para criar a pasta, necessário executar o comando:
```
mkdir /home/torizon/app
```
Após a criação da pasta é necessário copiar o binário executável `logpyx_warehouse_forklift` e o arquivo de configuração `config_forklift.json` para a pasta app criada no passo anterior.
Sugestão: no Linux pode ser usado o comando `scp` para transferir os arquivos via ssh:
```
scp logpyx_warehouse_forklift torizon@xxx.xxx.xxx.xxx:~/app
scp config_forklift.json torizon@xxx.xxx.xxx.xxx:~/app
```
xxx.xxx.xxx.xxx é o IP da Toradex Colibri IMX8X.

### Arquivo de Configuração (config_forklift.json)
No arquivo de configuração são ajustados alguns parâmetros essenciais:

`"operation_mode":` número que determina o modo de operação. 0 = solução armazém completa Logpyx; 1 = fornecimento apenas de dados de sensores;
`"uwb_net_id":` string hexadecimal indicando o PANID da rede UWB local. Esse valor é automaticamente repassado para as TAGs via BLE GATT;
`"ble_pos_ang_mac:` string com o MAC address do BLE do ESP32. É utilizado para a busca correta do dispositivo instalado na cabine da empilhadeira. Seus dois últimos bytes são usados como identificador da empilhadeira nas mensagens exportadas para o servidor;
`"manual_angular_compensation":` número que ativa/desativa a compensação angular entre o valor dado pelo sensor de orientação absoluta correspondente aos eixos das coordenadas definidas na rede UWB. 0=compensação automática, 1=compensação manual (mais confiável);
`"angle_compensation_deg":` número em graus da compensação angular, caso o campo anterior esteja selecionado (`"manual_angular_compensation": 1`).
`"dev_path_load_distance":` string com o endereço do sensor responsável por medir a distância até a carga,
`""dev_path_fork_height":"` string com o endereço do sensor responsável por medir a altura do garfo,
`"local_broker_addr":` string com o endereço do broker MQTT utilizado para receber os códigos de identificação da carga e exportação dos dados,
`"local_broker_port":` número da porta do broker MQTT,
`"dist_midpoint_to_load_sensor":` distância horizontal em mm do ponto médio entre as duas TAGs ao sensor de distância da carga;
`"dist_horizontal_center_load":` distância horizontal em mm entre o sensor de distância  e o centro da carga;
`"dist_vertical_center_load":` altura em mm do centro da carga;
`"loaded_threshold"`: número que representa o limiar de distância inferior em mm para considerar o estado carregado;
`"unloaded_threshold":` número que representa limiar de distância superior em mm para considerar o estado descarregado;
`"num_of_codes_ch":` número esperado de canais de códigos de carga;

Há valores padrões para todos os campos, caso não sejam preenchidos (vide config.c).

#### Exemplo do arquivo de configuração:
```json
{
 "operation_mode": 0,
  "uwb_net_id": "a269",
  "ble_pos_ang_mac": "94:B9:7E:D6:06:56",
  "manual_angular_compensation": 1,
  "angle_compensation_deg": 180,
  "dev_path_load_distance": "/dev/colibri-uartb",
  "dev_path_fork_height": "/dev/colibri-uartc",
  "local_broker_addr": "mqtt_broker",
  "local_broker_port": 1883,
  "dist_midpoint_to_load_sensor": 1500,
  "dist_horizontal_center_load": 713,
  "dist_vertical_center_load": 600,
  "loaded_threshold": 200,
  "unloaded_threshold": 500,
  "num_of_codes_ch": 1
}
```
### Download da imagem do container
Para baixar a imagem do container `jeadias/logpyx_warehouse_forklift`, basta fazer um docker pull:
```
docker pull jeadias/logpyx_warehouse_forklift
```
Certifique-se que a Toradex esteja com acesso à internet.

### Executando o container Logpyx Warehouse Forklift e o processamento principal.

Há 2 modos sugeridos:
* Rodar o container  jeadias/logpyx_warehouse_forklift e rodar o executável de processamento principal MANUALMENTE. (Útil para debug).
```
docker run --rm -it --device=/dev/colibri-uartb:/dev/colibri-uartb --device=/dev/colibri-uartc:/dev/colibri-uartc -v /var/run/dbus:/var/run/dbus -v /home/torizon/app:/app --network=lpx-net jeadias/logpyx_warehouse_forklift bash
```
O bash fica disponível para  rodar o executável de processamento principal:
```
cd /app
./logpyx_warehouse_forklift
```
* Rodar o container  jeadias/logpyx_warehouse_forklift em segundo plano e com início/reinício automático:
```
docker run -d --restart always --device=/dev/colibri-uartb:/dev/colibri-uartb --device=/dev/colibri-uartc:/dev/colibri-uartc -v /var/run/dbus:/var/run/dbus -v /home/torizon/app:/app --network=lpx-net --name logpyx_warehouse_forklift jeadias/logpyx_warehouse_forklift
```
O container irá parar de executar somente após o comando  `docker container stop logpyx_warehouse_forklift`. 
Para evitar que ele seja reiniciado após o reboot, necessário removê-lo com o comando  `docker container rm logpyx_warehouse_forklift`.

## Formatação dos dados enviados e recebidos em tempo real
A rotina de processamento principal envia e recebe dados de um broker MQTT interno. Os tópicos são locais e podem ser remapeados através de uma configuração em ponte (vide container broker MQTT) para a exportação de dados para um outro broker MQTT externo.
### Localização em tempo real
Quando selecionado `"operation_mode":0`, a rotina envia cada segundo as informações de localização, incluindo latitude, longitude e estado do carregamento para o tópico **lpx/warehouse/forklift/location**. A ideia é que o servidor externo use esta informação para gerar a animação de deslocamento/carregamento em tempo real.
#### Exemplo:
```json
{
	"tmst":	1646426909158,
	"dev_addr":	"0656",
	"position":	{
		"x":	10.234,
		"y":	24.864,
		"qf":	84,
		"angle": 182,
		"tmst":	1646426909060
	},
	"loaded":	0
}
```
### Eventos relacionados as cargas
Quando selecionado `"operation_mode":0`, 3 tipos de eventos relacionados as cargas são notificados:
* Carregamento (pick) - anterior ao reconhecimento do código da carga
#### Exemplo:
```json
{
	"tmst":	1646426970395,
	"dev_addr":	"0656",
	"evt_type":	"pick",
	"positions":	{
		"pick":	{
			"tmst":	1646426970394,
			"x":	5.221,
			"y":	4.545,
			"height": 1.545
		},
		"place":	{
			"tmst":	0,
			"x":	0,
			"y":	0,
			"height": 0
		}
	},
	"codes":	[{
			"ch":	0,
			"type":	"",
			"subtype":	"",
			"code":	""
		}]
}
```
* Carregamento (pick) - após o reconhecimento do código da carga
#### Exemplo:
```json
{
	"tmst":	1646427127301,
	"dev_addr":	"0656",
	"evt_type":	"pick",
	"positions":	{
		"pick":	{
			"tmst":	1646426970394,
			"x":	5.221,
			"y":	4.545,
			"height": 1.545
		},
		"place":	{
			"tmst":	0,
			"x":	0,
			"y":	0,
			"height": 0
		}
	},
	"codes":	[{
			"ch":	0,
			"type":	"rfid",
			"subtype":	" ISO/IEC18000",
			"code":	"1234759287482"
		},
		{
			"ch": 1,
			  "type": "barcode",
			  "subtype": "128CODE",
			 "code": "154524651555852"
		}]
}
```
A quantidade de canais de códigos é selecionada no arquivo de configurações com o parâmetro `"num_of_codes_ch"`.

* Descarregamento (place)
#### Exemplo:
```json
{
	"tmst":	1646427127301,
	"dev_addr":	"0656",
	"evt_type":	"pick",
	"positions":	{
		"pick":	{
			"tmst":	1646426970394,
			"x":	5.221,
			"y":	4.545,
			"height": 1.545
		},
		"place":	{
			"tmst":	1646426990548,
			"x":	8.251,
			"y":	4.415,
			"height": 0.755
		}
	},
	"codes":	[{
			"ch":	0,
			"type":	"rfid",
			"subtype":	" ISO/IEC18000",
			"code":	"1234759287482"
		},
		{
			"ch": 1,
			  "type": "barcode",
			  "subtype": "128CODE",
			 "code": "154524651555852"
		}]
}
```
Esses eventos são enviados para o tópico **lpx/warehouse/load/events**.

### Dados dos sensores
Algumas integrações com outras empresas (como a IHM) requerem somente o envio dos dados dos sensores. Quando selecionado `"operation_mode":1`,  no tópico **lpx/warehouse/forklift/rawdata** são enviadas as informações dos sensores.
#### Exemplo:
```json
{
	"tmst":	1646426499834,
	"location":	{
		"x":	-15.3953952,
		"y":	-42.8636768,
		"tmst":	1646426499059
	},
	"load":	{
		"distance":	3.05,
		"tmst":	1646426499810
	}
}
```
## Recepção de informações
### Códigos de identificação das cargas
A rotina de processamento principal recebe os códigos de identificação das cargas através do tópico **lpx/warehouse/recv/loadcodes**. Trata-se de um vetor de JSONs contendo o número do canal, a classificação do código e o código propriamente dito.
#### Exemplo:
```json
[ {
      "ch": 0,
      "type": "rfid",
      "subtype": " ISO/IEC18000",
      "code": "1234759287482"
  },
  {
      "ch": 1,
      "type": "barcode",
      "subtype": "128CODE",
      "code": "1"
  }
 ]
```

## Carregamento de configuração via MQTT
O sistema é capaz de receber o conteúdo do arquivo de configurações config_forklift.json através do tópico **lpx/warehouse/recv/config** e gravá-lo em arquivo.