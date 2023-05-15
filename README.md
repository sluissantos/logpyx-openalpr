
# LOGPYX PLATE RECOGNIZER
> Este documento detalha os passos necessários para rodar a rotina de processamento principal (Main processing) do Logpyx Plate Recognizer.

## 💻 Pré-Requisitos

Antes de começar, verifique se você atendeu aos seguintes requisitos:
* Materiais necessários:
	- Câmera IP conectada à rede.
	- Disposito usando Linux Ubuntu ou Docker com uma imagem Ubuntu.
* Caso a aplicação seja executada diretamente em uma distribuição Linux, é aconselhável que seja em Linux Ubunto. Para isso, é necessaŕio ter instalado as dependências listadas no arquivo `instal.sh`.
* Caso a aplicação seja executada em Docker, utilizar o arquivo dockerfile para gerar a imagem e o docker-compose para gerir o container.


### Configurações Inicias e Variáveis de Ambiente
Se a aplicação for executada diretamente em uma distribuição Linux (preferencialmente no Ubuntu), é necessário inicializar variáveis de ambiente para cada variável que será usada na aplicação.
Caso a aplicação seja executada usando Docker, definir essas variáveis no docker-compose.

`"IP_MQTT"` - Define o IP do broker MQTT para onde a placa será enviada. Nos casos de teste, o envio foi para o ambiente QA do revolog:
`IP_MQTT=gwqa.revolog.com.br`

`"PORT_MQTT"` - Define a porta do broker. Padrão do ambiente QA é 1884:
`PORT_MQTT=1884`

`"USER_NAME_MQTT"` - Variável que define o user do broker. Padrão é "teclogia":
`USER_NAME_MQTT=tecnologia`

`"PASSWORD_MQTT"` - Variável que define o passwd do broker. Padrão é a senha {padrao complexa}:
`PASSWORD_MQTT={padrao complexa}`

`"PUBLISH_TOPIC"` - Define o tópico de envio da placa encontrada:
`PUBLISH_TOPIC=aperam/plate`
Obs: a mensagem está com o seguinte padrão:
```json
{
	"plate":"RIO2022"
}
```

`"TESSERACT_GRAY"` - Essa variável define o fator em que a imagem original do frame será convertida para a escala cinza, usado como pré-processamento para o uso no Tesseract. O valor varia de acordo com a luminozidade do local. Nos teste realizados, foi definino como valor inicial o valor 130:
`TESSERACT_GRAY=130`

`"SCALE_FACTOR_CASCADE"` - Define o valor de incremento usado pela função Haar Cascade. Esse valor deve ser maior do que 1 (um) e afeta diretamente o tempo de processamento da imagem. Quanto mais próximo do valor 1, menor será o incremento e logo, maior será o tempo necessário para analisar o frame em questão. Contudo, quando menor o incremento, maior será a capacidade do algoritmo captar as coordenadas da placa na imagem. O valor inicial dessa variável foi defininido como 1.7:
`SCALE_FACTOR_CASCADE=1.7`

`"CAMERA_SOURCE"` - A partir de uma cãmera IP conectada à rede, é necessário obter as imagens em tempo real da mesma. Para ambas as formas de rodar a aplicação, a definição da variável de ambiente para câmeras da marca HIkVision seguem a seguinte fórmula:
`CAMERA_SOURCE=rtsp://{login}:{password}@{ip}/Streaming/channels/101`
Obs: para cada marca, existe uma forma diferente de definir o URL para obteção dos frames em tempo real. 

`"TIME_OUT_SEND_PLATE"` - Define o tempo, em segundos, de envio da placa encontrada para o broker MQTT. Quando uma placa é encontrada pela aplicação, ela é armazenada em uma lista e processada. A partir desse momento, caso a aplicação não reconheça mais nenhuma placa, é inicializado um timer. Caso esse timer exceda o valor de timeout, é enviada a placa encontrada para o borker e limpado o buffer. Valor inicial de 5 segundos:
`TIME_OUT_SEND_PLATE=5`

``"MIN_LINE_FRAME"` e `"MAX_LINE_FRAME"`` -  Esses valores definem o mínimo e máximo de pixels que serão usados pelo Cascade. Isso "corta" o frame em certo ponto. Quanto menor o tamanho da imagem, mais rápido será o algoritmo de procura. O ideal é que defina na imagem um padrão de onde as placas podem aparecer e minorar o máximo possível o tamanho da imagem:
`MIN_LINE_FRAME=100`
`MAX_LINE_FRAME=900`


### Executando a aplicação usando Docker
Para realizar a criação da imagem, rodar os seguinte comando: 
`docker build -t {nome da imagem}:{versao da imagem} .`
Obs: o padrão utilizado foi **docker build -t logpyx/aperam:1.0 .**
Obs: a aplicação não pode ser executada usando **docker run**, uma vez que as variáveis de ambiente necessárias para a execução do mesmo só são inicializadas no docker-compose.

Para executar o docker-compose:
`docker compose up`
Obs: esse comando deve ser executado no diretório onde o docker-compose está.

Obs: nos testes, o terminal não exibia as placas encontradas tanto pelo Tesseract quanto pelo Alpr. Contudo, foi evidenciado que a aplicação está funcionando, quando monitorado o envio da placa para o broker.

### Executando a aplicação usando Linux Ubuntu
Após realizar a execução do arquivo install.sh com o comando:
`sudo bash install.sh`

Para rodar a aplicação, basta rodar:
`sudo python3 /home/logpyx-openalpr/DetectionPlate.py`

### Detalhamento da configuração da função Cascade
Ao baixar o repositório, há dois diretórios que são usados para configurações de funções que são usadas na aplicação. 
O diretório `runtime_date` e `config` presente em **/logpyx-openalpr** define os parâmetros que serão usados pelas funções. É necessário um estudo e análise desses parâmetros, uma vez que para cada cenário do uso dessa aplicação essas variáveis devem ser reajustadas. É extremamente significativo o impacto no desempenho da aplicação a depender dessas configurações.