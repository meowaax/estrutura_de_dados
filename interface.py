import streamlit as st
import heapq
from datetime import datetime
from collections import deque


class Passageiro:
    def __init__(self, nome, documento, assento):
        self.nome = nome
        self.documento = documento
        self.assento = assento
    
    def __str__(self):
        return (f"Nome: {self.nome}, Documento: {self.documento}, Assento: {self.assento}")


class ListaPassageiros:
    def __init__(self):
        self.hash_table = {}

    def adicionar_passageiro(self, passageiro):
        self.hash_table[passageiro.documento] = passageiro

    def remover_passageiro(self, documento):
        if documento in self.hash_table:
            self.hash_table.pop(documento)
            return True
        else:
            print('Passageiro não encontrado.')
            return False

    def listar_passageiros(self):
        lista = []
        for documento, passageiro in self.hash_table.items():
            lista.append(str(passageiro))
        
        return lista

    def buscar_passageiro_por_documento(self, documento):
        return self.hash_table.get(documento, None)
    

class Voo:
    def __init__(self, id_voo, origem, destino, data, num_assentos, custo):
        self.id_voo = id_voo
        self.origem = origem
        self.destino = destino
        self.data = datetime.strptime(data, '%Y-%m-%d')
        self.num_assentos = num_assentos
        self.assentos_disponiveis = num_assentos
        self.passageiros = ListaPassageiros()
        self.custo = custo  # Novo campo para o custo do voo

    def adicionar_passageiro(self, passageiro):
        if self.assentos_disponiveis > 0:
            self.passageiros.adicionar_passageiro(passageiro)
            self.assentos_disponiveis -= 1
            return True
        return False

    def remover_passageiro(self, documento):
        if self.passageiros.remover_passageiro(documento):
            self.assentos_disponiveis += 1
            return True
        return False

    def listar_passageiros(self):
        passageiros = self.passageiros.listar_passageiros()
        return passageiros
    
    def __str__(self):
        return (f"Voo ID: {self.id_voo}\n"
                f"Origem: {self.origem}\n"
                f"Destino: {self.destino}\n"
                f"Data: {self.data.strftime('%d/%m/%Y')}\n"
                f"Total de assentos: {self.num_assentos}\n"
                f"Assentos disponíveis: {self.assentos_disponiveis}\n"
                f"Custo: {self.custo}")


class ListaVoos:
    def __init__(self):
        self.hash_table = {}

    def adicionar_voo(self, voo):
        self.hash_table[voo.id_voo] = voo

    def remover_voo(self, id_voo):
        if id_voo in self.hash_table:
            self.hash_table.pop(id_voo)
            return True
        else:
            print('Voo não encontrado.')
            return False

    def buscar_voo_por_id(self, id_voo):
        voo = self.hash_table.get(id_voo, None)
        return voo 

    
    def listar_voos(self):
        lista = []
        for id_voo, voo in self.hash_table.items():
            lista.append(str(voo))
        return lista

    def busca_em_largura(self, origem, destino):
        visitados = set()
        fila = deque([(origem, [])])  # Inicializa a fila com origem e uma lista vazia para IDs de voos

        while fila:
            atual, ids_voos = fila.popleft()  # Remove o elemento da frente da fila

            if atual == destino:
                return ids_voos  # Retorna a lista de IDs de voos que conectam origem e destino

            if atual not in visitados:
                visitados.add(atual)

                # Itera pelos voos da hash_table para encontrar os vizinhos (voos conectados)
                for voo in self.hash_table.values():
                    if voo.origem == atual and voo.destino not in visitados:
                        # Adiciona o destino do voo à fila, junto com o ID do voo associado
                        fila.append((voo.destino, ids_voos + [voo.id_voo]))

        return None  # Retorna None se não houver caminho entre origem e destino
    
    # Implementando Dijkstra para encontrar o caminho mais barato
    def dijkstra(self, origem, destino):
        # Inicializa as distâncias como infinito para todas as cidades
        distancias = {cidade: float('inf') for cidade in set([voo.origem for voo in self.hash_table.values()] + [voo.destino for voo in self.hash_table.values()])}
        distancias[origem] = 0
        
        # Anteriores guardam tanto a cidade anterior quanto o ID do voo usado
        anteriores = {cidade: (None, None) for cidade in distancias}
        fila_prioridade = [(0, origem)]  # Fila de prioridade inicializada com a origem

        while fila_prioridade:
            distancia_atual, cidade_atual = heapq.heappop(fila_prioridade)

            # Se chegamos ao destino, reconstruímos o caminho
            if cidade_atual == destino:
                caminho_cidades = []
                caminho_voos = []
                while cidade_atual:
                    caminho_cidades.append(cidade_atual)
                    cidade_atual, voo_id = anteriores[cidade_atual]
                    if voo_id:
                        caminho_voos.append(voo_id)  # Adiciona o ID do voo ao caminho
                return caminho_cidades[::-1], caminho_voos[::-1], distancias[destino]  # Retorna o caminho, os voos e a distância total

            # Explora os vizinhos (voos saindo da cidade atual)
            for voo in self.hash_table.values():
                if voo.origem == cidade_atual:
                    nova_distancia = distancia_atual + voo.custo  # Assume que voo.custo é o peso da aresta
                    if nova_distancia < distancias[voo.destino]:
                        distancias[voo.destino] = nova_distancia
                        anteriores[voo.destino] = (cidade_atual, voo.id_voo)  # Salva a cidade anterior e o ID do voo
                        heapq.heappush(fila_prioridade, (nova_distancia, voo.destino))

        return None, None, float('inf')  # Retorna None se não houver caminho

st.set_page_config(
    page_title="FlyHigh",
    page_icon=":airplane:",
)

lista_voos = ListaVoos()

if 'lista_voos' not in st.session_state:
    voos_exemplo = [
    Voo(101, "São Paulo", "Rio de Janeiro", "2024-09-01", 150, 200.50),
    Voo(102, "São Paulo", "Belo Horizonte", "2024-09-02", 120, 180.00),
    Voo(103, "Brasília", "Salvador", "2024-09-03", 140, 250.00),
    Voo(104, "Rio de Janeiro", "Recife", "2024-09-04", 160, 300.00),
    Voo(105, "Recife", "Fortaleza", "2024-09-05", 180, 220.00),
    Voo(106, "Fortaleza", "Manaus", "2024-09-06", 170, 350.00),
    Voo(107, "Manaus", "Belém", "2024-09-07", 130, 270.00),
    Voo(108, "Belém", "São Paulo", "2024-09-08", 110, 450.00),
    Voo(109, "Curitiba", "Porto Alegre", "2024-09-09", 100, 160.00),
    Voo(110, "Porto Alegre", "São Paulo", "2024-09-10", 140, 210.00),
    Voo(111, "Florianópolis", "Curitiba", "2024-09-11", 120, 190.00),
    Voo(112, "São Paulo", "Brasília", "2024-09-12", 150, 230.00),
    Voo(113, "Rio de Janeiro", "Salvador", "2024-09-13", 140, 260.00),
    Voo(114, "Belo Horizonte", "Recife", "2024-09-14", 130, 300.00),
    Voo(115, "Salvador", "Porto Alegre", "2024-09-15", 140, 320.00),
    Voo(116, "Recife", "Manaus", "2024-09-16", 160, 350.00),
    Voo(117, "Fortaleza", "Rio de Janeiro", "2024-09-17", 170, 280.00),
    Voo(118, "Belém", "São Paulo", "2024-09-18", 150, 400.00),
    Voo(119, "Curitiba", "Salvador", "2024-09-19", 140, 270.00),
    Voo(120, "Porto Alegre", "Recife", "2024-09-20", 130, 310.00),
    Voo(121, "Manaus", "São Paulo", "2024-09-21", 120, 420.00),
    Voo(122, "São Paulo", "Fortaleza", "2024-09-22", 150, 380.00),
    Voo(123, "Brasília", "Curitiba", "2024-09-23", 140, 260.00),
    Voo(124, "Recife", "Belo Horizonte", "2024-09-24", 160, 290.00),
    Voo(125, "Salvador", "Brasília", "2024-09-25", 140, 250.00),
    Voo(126, "Rio de Janeiro", "Manaus", "2024-09-26", 130, 320.00),
    Voo(127, "São Paulo", "Belém", "2024-09-27", 120, 410.00),
    Voo(128, "Curitiba", "Rio de Janeiro", "2024-09-28", 150, 230.00),
    Voo(129, "Porto Alegre", "Fortaleza", "2024-09-29", 140, 350.00),
    Voo(130, "Manaus", "Salvador", "2024-09-30", 160, 340.00),
    Voo(131, "Fortaleza", "São Paulo", "2024-10-01", 170, 300.00),
    Voo(132, "Recife", "São Paulo", "2024-10-02", 140, 370.00),
    Voo(133, "Belém", "Brasília", "2024-10-03", 150, 360.00),
    Voo(134, "Brasília", "Fortaleza", "2024-10-04", 120, 280.00),
    Voo(135, "Rio de Janeiro", "Porto Alegre", "2024-10-05", 110, 320.00),
    Voo(136, "São Paulo", "Curitiba", "2024-10-06", 130, 190.00),
    Voo(137, "Salvador", "Rio de Janeiro", "2024-10-07", 120, 240.00),
    Voo(138, "Brasília", "Recife", "2024-10-08", 150, 270.00),
    Voo(139, "Belo Horizonte", "São Paulo", "2024-10-09", 140, 220.00),
    Voo(140, "Curitiba", "Manaus", "2024-10-10", 130, 410.00),
    Voo(141, "Fortaleza", "Salvador", "2024-10-11", 120, 350.00),
    Voo(142, "São Paulo", "Recife", "2024-10-12", 160, 390.00),
    Voo(143, "Rio de Janeiro", "Belo Horizonte", "2024-10-13", 150, 180.00),
    Voo(144, "Porto Alegre", "Manaus", "2024-10-14", 140, 370.00),
    Voo(145, "Brasília", "São Paulo", "2024-10-15", 160, 290.00),
    Voo(146, "Curitiba", "Fortaleza", "2024-10-16", 130, 310.00),
    Voo(147, "Manaus", "Recife", "2024-10-17", 120, 400.00),
    Voo(148, "Fortaleza", "Brasília", "2024-10-18", 150, 290.00),
    Voo(149, "São Paulo", "Porto Alegre", "2024-10-19", 170, 320.00),
    Voo(150, "Recife", "Salvador", "2024-10-20", 140, 300.00),
    ]
    st.session_state.lista_voos = ListaVoos()
    for voo in voos_exemplo:
        st.session_state.lista_voos.adicionar_voo(voo)


# Streamlit
st.title('🛫FlyHigh')
st.header('Sistema de Reserva de Voos')

with st.form('busca_voo', clear_on_submit=True): #Buscar voos a partir da origem e destino
    st.subheader('Buscar Voos')
    origem = st.text_input('Origem')
    destino = st.text_input('Destino')
    radio = st.radio('Tipo de busca', ['Menor caminho', 'Menor custo'], index=None)
    submit = st.form_submit_button('Buscar')
    
    if submit:
        if radio == 'Menor caminho':
            rota = st.session_state.lista_voos.busca_em_largura(origem, destino)
            st.write(f'Rota encontrada: {rota}')
            st.subheader('Detalhes:')
            if rota:
                for voo in rota:
                    voo_encontrado = st.session_state.lista_voos.buscar_voo_por_id(voo)
                    if voo_encontrado:
                        st.text_area(f"{voo_encontrado.id_voo}", str(voo_encontrado), height=200)
                        st.divider()
            else:
                st.write('Não há voos disponíveis para esse trajeto. ❌')
        elif radio == 'Menor custo':
            caminho, voos, custo = st.session_state.lista_voos.dijkstra(origem, destino)
            st.write(f'Caminho: {caminho}, Id voos: {voos}, Custo: {custo}')
            st.subheader('Detalhes:')
            if caminho: 
                for voo in voos:
                    voo_encontrado = st.session_state.lista_voos.buscar_voo_por_id(voo)
                    if voo_encontrado:
                        st.text_area(f"{voo_encontrado.id_voo}", str(voo_encontrado), height=200)
                        st.divider()
            else:
                st.write('Não há voos disponíveis para esse trajeto. ❌')
        else:
            st.write('Por favor, selecione uma das opções. 😄')

with st.form('reservar_voo', clear_on_submit=True): #Reserva de voos
    st.subheader('Reservar Voo')
    id_voo = st.text_input('Id voo')
    nome = st.text_input('Nome passageiro')
    documento = st.text_input('Documento passageiro')
    assento = st.text_input('Número assento')
    submitted = st.form_submit_button('Reservar voo')
    
    if submitted:
        voo = st.session_state.lista_voos.buscar_voo_por_id(int(id_voo))
        if voo:
            passageiro = Passageiro(nome, documento, assento)
            voo.adicionar_passageiro(passageiro)
            st.write('Reserva realizada com sucesso! ✔️😄')
        else:
            st.write('Algo deu errado 😭 Por favor, tente novamente.')

with st.form('listar_passageiros', clear_on_submit=True): #Listar passageiros
    st.subheader('Listar passageiros')
    id_voo = st.text_input('Id voo')
    submitted = st.form_submit_button('Listar passageiros')
    
    if submitted:
        voo = st.session_state.lista_voos.buscar_voo_por_id(int(id_voo))
        if voo:
            st.subheader(f'Passageiros do Voo {voo.id_voo} ({voo.origem}) -> ({voo.destino})')
            passageiros = voo.listar_passageiros()
            if passageiros:
                for passageiro in passageiros:
                    st.write(passageiro)
                    st.divider()
            else:
                st.write('Nenhum passageiro encontrado. 😞')


st.subheader('Lista de Voos')

if st.button('Listar voos', type="primary"): #Listar voos
    voos = st.session_state.lista_voos.listar_voos()
    for voo in voos:
        st.write(voo)
        st.divider()
