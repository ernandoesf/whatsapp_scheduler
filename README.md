# Atendente Automático WhatsApp para Eletricista com Agendamento no Google Agenda

## 1. Introdução

Este projeto implementa um atendente automático via WhatsApp, projetado especificamente para eletricistas, com a capacidade de interagir com clientes, coletar informações essenciais e agendar automaticamente serviços no Google Agenda. O bot visa otimizar o processo de agendamento, proporcionando uma experiência fluida e eficiente tanto para o cliente quanto para o profissional.

## 2. Funcionalidades

O bot oferece as seguintes funcionalidades:

*   **Saudação Automática**: Responde a novas mensagens no WhatsApp de forma imediata.
*   **Coleta de Dados do Cliente**: Solicita e armazena nome, endereço e descrição do problema elétrico.
*   **Verificação de Disponibilidade**: Consulta a agenda do eletricista no Google Calendar para encontrar horários livres.
*   **Oferta de Horários**: Apresenta ao cliente opções de datas e horários disponíveis.
*   **Confirmação de Agendamento**: Permite ao cliente confirmar o horário escolhido.
*   **Criação de Evento no Google Agenda**: Cria um evento detalhado na agenda do eletricista com todas as informações coletadas.
*   **Confirmação via WhatsApp**: Envia uma mensagem de confirmação ao cliente após o agendamento.
*   **Notificação ao Eletricista**: Garante que o eletricista seja informado sobre novos agendamentos.
*   **Persistência de Conversa**: Mantém o estado da conversa, permitindo que o cliente retome de onde parou.
*   **Cancelamento Flexível**: Permite ao cliente cancelar o agendamento a qualquer momento.

## 3. Tecnologias Utilizadas

As principais tecnologias empregadas neste projeto são:

*   **Python**: Linguagem de programação principal.
*   **Flask**: Microframework web para o backend da aplicação.
*   **SQLite**: Banco de dados leve para persistência do estado da conversa.
*   **WhatsApp API**: Para comunicação com o WhatsApp (compatível com Evolution API, Meta Cloud API ou similar).
*   **Google Calendar API**: Para gerenciamento de agendamentos.
*   **python-dotenv**: Para gerenciamento de variáveis de ambiente.
*   **requests**: Para fazer requisições HTTP.

## 4. Estrutura do Projeto

A estrutura de diretórios do projeto é organizada da seguinte forma:

```
whatsapp_scheduler/
├── app/
│   ├── __init__.py
│   ├── main.py             # Aplicação Flask principal e webhook
│   ├── models.py           # Gerenciamento de sessão e banco de dados SQLite
│   └── bot_logic.py        # Lógica do fluxo conversacional (máquina de estados)
├── data/
│   └── database.sqlite     # Banco de dados SQLite (criado automaticamente)
├── tests/
│   └── test_flow.py        # Script para simular o fluxo de conversa
├── utils/
│   ├── __init__.py
│   ├── calendar_api.py     # Funções para interação com Google Calendar API
│   └── whatsapp_api.py     # Funções para interação com WhatsApp API
├── .env.example            # Exemplo de arquivo de variáveis de ambiente
├── requirements.txt        # Dependências do projeto
└── README.md               # Documentação do projeto
```

## 5. Configuração do Ambiente

Para configurar e rodar o projeto, siga os passos abaixo:

### 5.1. Pré-requisitos

Certifique-se de ter o Python 3.8+ e `pip` instalados em seu sistema.

### 5.2. Instalação de Dependências

Navegue até o diretório raiz do projeto e instale as dependências:

```bash
pip install -r requirements.txt
```

### 5.3. Configuração do Google Cloud para Google Calendar API

1.  Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2.  Crie um novo projeto ou selecione um existente.
3.  No menu de navegação, vá para **APIs e Serviços > Biblioteca**.
4.  Procure por "Google Calendar API" e habilite-a.
5.  No menu de navegação, vá para **APIs e Serviços > Credenciais**.
6.  Clique em "Criar Credenciais" e selecione "ID do cliente OAuth".
7.  Selecione "Aplicativo de desktop" como tipo de aplicativo e dê um nome.
8.  Após a criação, faça o download do arquivo `credentials.json`. Renomeie-o para `credentials.json` e coloque-o na raiz do diretório `whatsapp_scheduler`.
    *   **Importante**: Este arquivo contém suas credenciais de API e deve ser mantido seguro. Para produção, o fluxo de autenticação OAuth 2.0 para aplicações web é recomendado.

### 5.4. Configuração da WhatsApp API

Este projeto é compatível com diversas APIs de WhatsApp (ex: Evolution API, Meta Cloud API). Você precisará de uma conta e credenciais de uma dessas plataformas.

1.  Obtenha sua URL da API, chave de API (API Key) e ID da instância (Instance ID) da plataforma de WhatsApp que você escolheu.
2.  Essas informações serão usadas no arquivo `.env`.

### 5.5. Configuração do Arquivo `.env`

Crie um arquivo chamado `.env` na raiz do diretório `whatsapp_scheduler` (o mesmo nível do `README.md`) e preencha-o com suas credenciais, usando o `.env.example` como base:

```ini
# Configurações da API do WhatsApp (Exemplo: Evolution API)
WHATSAPP_API_URL=https://sua-instancia.com
WHATSAPP_API_KEY=seu_token_aqui
WHATSAPP_INSTANCE_ID=nome_da_instancia

# Flask Config
FLASK_APP=app/main.py
FLASK_ENV=development
PORT=5000
```

*   Substitua `https://sua-instancia.com`, `seu_token_aqui` e `nome_da_instancia` pelos valores reais da sua API do WhatsApp.

## 6. Como Rodar o Serviço

Após configurar o ambiente e as credenciais, você pode iniciar o servidor Flask:

```bash
flask run --host=0.0.0.0 --port=$PORT
```

O servidor será iniciado na porta especificada no seu arquivo `.env` (padrão: 5000). Você precisará configurar um webhook na sua plataforma de WhatsApp para apontar para `http://seu_servidor:porta/webhook`.

## 7. Fluxo Conversacional

O bot segue um fluxo conversacional estruturado para coletar as informações necessárias e agendar o serviço:

1.  **Saudação Inicial**: O bot cumprimenta o cliente e pede o nome.
2.  **Coleta de Endereço**: Solicita o endereço para o atendimento.
3.  **Descrição do Problema**: Pede ao cliente para descrever o problema elétrico.
4.  **Verificação de Agenda**: O bot consulta o Google Agenda do eletricista para encontrar horários disponíveis (próximos 5 dias úteis, das 08:00 às 18:00, com horários fixos de exemplo).
5.  **Oferta de Opções**: Apresenta uma lista numerada de horários livres.
6.  **Confirmação**: Após a escolha do cliente, o bot resume as informações e pede confirmação.
7.  **Criação de Evento**: Se confirmado, um evento é criado no Google Agenda com os detalhes do serviço.
8.  **Confirmação Final**: O bot envia uma mensagem de confirmação ao cliente.

**Regras Importantes:**

*   O bot mantém o estado da conversa. Se o cliente demorar para responder, ele continuará de onde parou.
*   Se o cliente digitar algo inesperado, o bot repetirá a pergunta atual.
*   Se o horário escolhido ficar indisponível antes da confirmação, o bot recalculará as opções.
*   O cliente pode digitar "cancelar" a qualquer momento para reiniciar o fluxo.

## 8. Cenários de Teste

Um script de simulação está disponível para testar o fluxo do bot sem a necessidade de uma integração real com WhatsApp ou Google Calendar (que são mockados no script de teste).

Para executar a simulação:

```bash
python tests/test_flow.py
```

Este script simula uma conversa completa, incluindo:

*   Cliente agenda com sucesso.
*   (Outros cenários como cliente escolhe horário inválido, cliente para no meio e volta depois, cliente cancela, horário fica indisponível durante o fluxo, podem ser adicionados ou simulados manualmente editando o script `test_flow.py`)

## 9. Considerações Finais

Este projeto fornece uma base robusta para um atendente automático de WhatsApp. Para uso em produção, é crucial considerar:

*   **Segurança**: Implementar autenticação e autorização robustas para a API do WhatsApp e Google Calendar.
*   **Escalabilidade**: O SQLite é adequado para pequenos volumes de dados; para maior escala, considere bancos de dados como PostgreSQL ou MySQL.
*   **Tratamento de Erros**: Melhorar o tratamento de erros e logging para depuração e monitoramento.
*   **Flexibilidade de Horários**: A lógica de `get_free_slots` é simplificada. Para um sistema mais robusto, seria necessário um algoritmo mais sofisticado para encontrar horários livres, considerando durações de serviço, buffers entre agendamentos, etc.
*   **Integração Real**: A integração com a API do WhatsApp é um mock no ambiente de teste. Para uso real, é necessário configurar a API de sua escolha (Evolution API, Meta Cloud API, etc.) e o webhook correspondente.

---

**Autor:** Manus AI
**Data:** 27 de Abril de 2026
