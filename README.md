
# LOGPYX PLATE RECOGNIZER
> Este documento detalha os passos necessários para rodar a rotina de processamento principal (Main processing) do Logpyx Plate Recognizer.

## 💻 Pré-Requisitos

Antes de começar, verifique se você atendeu aos seguintes requisitos:
* Materiais necessários:
	- Câmera IP conectada à rede.
	- Disposito usando Linux Ubuntu ou Docker com uma imagem Ubuntu. É necessário que a versão Ubuntu utilizada seja no mínimo a 20.04.
* Caso a aplicação seja executada diretamente em uma distribuição Linux, é aconselhável que seja em Linux Ubuntu. Para isso, é necessaŕio ter instalado as dependências listadas no arquivo `instal.sh`.
* Caso a aplicação seja executada em Docker, utilizar o arquivo dockerfile para gerar a imagem e o docker-compose para gerir o container.


### Configurações Inicias e Variáveis de Ambiente
Se a aplicação for executada diretamente em uma distribuição Linux (preferencialmente no Ubuntu), é necessário inicializar variáveis de ambiente para cada variável que será usada na aplicação. Quando a aplicação é inicializada, essas variáveis são procuradas e, caso encontradas, seus valores são usados na aplicação. Uma vez que essa variável não é inserida como uma variável de ambiente, há valores padrão setados dentro da aplicação.

Caso a aplicação seja executada usando Docker, definir essas variáveis no docker-compose.

`"IP_MQTT"` - Define o IP do broker MQTT para onde a placa será enviada. Nos casos de teste, o envio foi para o ambiente QA do revolog:
`IP_MQTT: gwqa.revolog.com.br`

`"PORT_MQTT"` - Define a porta do broker. Padrão do ambiente QA é 1884:
`PORT_MQTT: 1884`

`"USER_NAME_MQTT"` - Variável que define o user do broker. Padrão é "teclogia":
`USER_NAME_MQTT: tecnologia`

`"PASSWORD_MQTT"` - Variável que define o passwd do broker. Padrão é a senha {padrao complexa}:
`PASSWORD_MQTT: {padrao complexa}`

`"PUBLISH_TOPIC"` - Define o tópico de envio da placa encontrada:
`PUBLISH_TOPIC: aperam/plate`

`"PUBLISH_TOPIC_STATUS"` - Define o tópico de envio da placa encontrada:
`PUBLISH_TOPIC_STATUS: aperam/plate/status`

`"TESSERACT_GRAY"` - Essa variável define o fator em que a imagem original do frame será convertida para a escala cinza, usado como pré-processamento para o uso no Tesseract. O valor varia de acordo com a luminozidade do local. Nos teste realizados, foi definino como valor inicial o valor 130:
`TESSERACT_GRAY: 130`

`"SCALE_FACTOR_CASCADE"` - Define o valor de incremento usado pela função Haar Cascade. Esse valor deve ser maior do que 1 (um) e afeta diretamente o tempo de processamento da imagem. Quanto mais próximo do valor 1, menor será o incremento e logo, maior será o tempo necessário para analisar o frame em questão. Contudo, quando menor o incremento, maior será a capacidade do algoritmo captar as coordenadas da placa na imagem. O valor inicial dessa variável foi defininido como 1.5:
`SCALE_FACTOR_CASCADE: 1.5`

`"CAMERA_SOURCE"` - A partir de uma cãmera IP conectada à rede, é necessário obter as imagens em tempo real da mesma. Para ambas as formas de rodar a aplicação, a definição da variável de ambiente para câmeras da marca HIkVision seguem a seguinte fórmula:
`CAMERA_SOURCE: rtsp://{login}:{password}@{ip}/Streaming/channels/101`
Obs: para cada marca, existe uma forma diferente de definir o URL para obteção dos frames em tempo real. 

`"TIME_OUT_SEND_PLATE"` - Define o tempo, em segundos, de envio da placa encontrada para o broker MQTT. Quando uma placa é encontrada pela aplicação, ela é armazenada em uma lista e processada. A partir desse momento, caso a aplicação não reconheça mais nenhuma placa, é inicializado um timer. Caso esse timer exceda o valor de timeout definido aqui, é enviada a placa encontrada para o borker e limpado o buffer. Valor inicial de 5 segundos:
`TIME_OUT_SEND_PLATE: 5`

``"MIN_LINE_FRAME"` e `"MAX_LINE_FRAME"`` -  Esses valores definem o mínimo e máximo de pixels que serão usados pelo Cascade. Isso "corta" o frame em certos pontos. Quanto menor o tamanho da imagem, mais rápido será o algoritmo de procura. O ideal é que defina na imagem um padrão de onde as placas podem aparecer e minorar o máximo possível o tamanho da imagem:
`MIN_LINE_FRAME: 200`
`MAX_LINE_FRAME: 900`

`"MAX_PLATES` - Esse valor define o número máximo de placas lidas e que serão enviadas para o broker. Uma vez que a aplicação esteja em execução, caso o buffer de placas lidas seja maior que o número máximo de placas definido aqui, a placa final encontrada será enviada para o broker.
`MAX_PLATES: 100`

`"FRAME_STEP` - Aqui definimos o passo de quantos em quantos frames colidos pela aplicação serão inseridos na fila de frames que serão analisados pelo algoritmo. Esse parâmetro tem relação direta com o delay da aplicação em relação ao vídeo em tempo real. Definindo como 1, todo frame recebido será incluído na fila. Caso, por exemplo, seja definido como 5, a cada 5 frames recolhidos, apenas 1 será incluido na fila para análise.
`FRAME_STEP: 1`

`"TIME_BETWEEN_READINGS"` - Esse parâmetro define o tempo, em segundos, em que a aplicação irá ficar em "sleep" após o envio de uma placa. Esse valor deve ser definido de acordo com a dinâmica de leitura exigida. Definindo com 10, após o envio de uma placa, seja por TIME_OUT_SEND_PLATE ou MAX_PLATES, a aplicação ficará em modo "sleep" por 10 segundos. Após esse período de tempo, a aplicação será "acordada".
`TIME_BETWEEN_READINGS: 10`

### Executando a aplicação usando Docker
Para realizar a criação da imagem, rodar os seguinte comando: 
`docker build -t {nome da imagem}:{versao da imagem} .`
Obs: o padrão utilizado foi **docker build -t logpyx/aperam:1.0 .**
Obs: a aplicação pode ser executada usando **docker run** para debug.

Para executar o docker-compose:
`docker compose up`
Obs: esse comando deve ser executado no diretório onde o docker-compose está.
**IMPORTANTE: A imgaem docker é grande, em torno de 2GB após ser finalizada. Consulte as concidções do servidor para verificar essa disponibilidade.**
**IMPORTANTE: No docker-compose utilizado como exemplo, é definido que todos os processadores da máquina (no caso, a máquina em questão possui 8 processadores) serão usados pelo container. Esse comando é de suma importância para definir um bom tempo de processamento da aplicação. É aconselhável setar todos os processadores disponíveis para serem usados pela aplicação.**
**IMPORTANTE: Numa tentativa de aumentar o desempenho da aplicação, foram efetuados testes onde foram criadas mais de 1 thread para a função que coletam o frame e para a funcão que realizada o put do frame e o processa. Contudo, nos testes realizados, não foram identificadas melhorias significativas, mas ainda vale uma nova tentativa.**

Obs: nos testes, o terminal não exibia as placas encontradas tanto pelo Tesseract quanto pelo Alpr. Contudo, foi evidenciado que a aplicação está funcionando, quando monitorado o envio da placa para o broker.

### Executando a aplicação usando Linux Ubuntu
Após realizar a execução do arquivo install.sh com o comando:
`sudo bash install.sh`

Para rodar a aplicação, basta rodar:
`sudo python3 $PATH/logpyx-openalpr/DetectionPlate.py`

### Detalhamento da configuração da função Cascade
Ao baixar o repositório, há dois diretórios que são usados para configurações de funções que são usadas na aplicação. 
O diretório `runtime_date` e `config` presente em **/logpyx-openalpr/openalpr** define os parâmetros que serão usados pelas funções. É necessário um estudo e análise desses parâmetros, uma vez que para cada cenário do uso dessa aplicação essas variáveis devem ser reajustadas. É extremamente significativo o impacto no desempenho da aplicação a depender dessas configurações. 
Nos testes realizados, foram testados diversas combinações de parâmetros, setados como padrão nessa aplicação.

### Padrões de mensageria no Broker MQTT
A cada 30 segundos, é enviado a seguinte mensagem de status no tópico defino pela variável `PUBLISH_TOPIC_STATUS`:
```
{
"tmst": 1697814638,
"ip": "10.50.239.20/Streaming/channels/101",
"status": true
}
```
O objeto `tmst` referencia o tempo atual.
O objeto `id` referencia o ip usado pela aplicação para ter acesso à câmera. Serve como identificação.
O objeto `status` refencia a conexão com a câmera. Caso a conexão com a câmera seja perdida, esse valor será setado para 'false'.

Agora, temos a seguinte mensagem JSON quando é enviada uma placa para o broker:
```json
{
"id": "10.50.239.20/Streaming/channels/101", 
"plate": "EUL0433"
}
```
O objeto `id` referencia o ip usado pela aplicação para ter acesso à câmera. Serve como identificação.
O objeto `plate` referencia a placa encontra pela aplicação. Uma mesma placa não será enviada duas vezes consecutivamente para o broker.