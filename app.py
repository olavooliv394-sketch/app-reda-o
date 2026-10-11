import os
import time
import datetime
import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. Configuração da página
st.set_page_config(
    page_title="Oficina de Redação | Professor Digital",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Estilização CSS Nativa e Refinada
st.markdown("""
<style>
    .main-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        margin-bottom: 0px;
    }
    
    div[data-testid="stExpander"] {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        margin-bottom: 8px;
    }
    
    div[data-testid="stExpander"] summary p {
        font-weight: 600;
    }

    .texto-consolidado {
        background-color: rgba(128, 128, 128, 0.08);
        border-left: 4px solid #17a2b8;
        padding: 16px;
        border-radius: 6px;
        font-size: 1.05rem;
        line-height: 1.6;
        font-family: 'Georgia', serif;
        margin-bottom: 15px;
    }

    .card-nota1000 {
        background-color: rgba(128, 128, 128, 0.05);
        border-left: 4px solid #28a745;
        padding: 18px;
        border-radius: 8px;
        font-family: 'Georgia', serif;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-bottom: 15px;
    }

    .card-carta {
        background-color: rgba(128, 128, 128, 0.05);
        border-left: 4px solid #ffc107;
        padding: 18px;
        border-radius: 8px;
        font-family: 'Georgia', serif;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-bottom: 15px;
    }

    .timer-box {
        background-color: rgba(23, 162, 184, 0.1);
        border: 1px solid rgba(23, 162, 184, 0.3);
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Verificação da Chave de API
if not os.environ.get("GEMINI_API_KEY"):
    st.error("⚠️ A chave GEMINI_API_KEY não foi configurada no terminal!")
    st.info("No terminal, execute: set GEMINI_API_KEY=sua_chave (Windows) ou export GEMINI_API_KEY=sua_chave (Mac/Linux).")
    st.stop()

# --- BANCO DE DADOS LOCAL EXPANDIDO (REDAÇÕES + CARTAS DO LEITOR) ---
REDACOES_NOTA_1000 = [
    # ------------------ CARTAS DO LEITOR ------------------
    {
        "id": 11,
        "genero": "Carta do Leitor",
        "ano": "Modelo Exemplar",
        "eixo": "💻 Tecnologia & Comunicação",
        "tema": "Reação à reportagem 'O impacto das telas no desenvolvimento infantil'",
        "texto": """<b>[Vocativo]</b> Prezada Redação da Revista Educação & Sociedade,<br><br>
        <b>[Referência]</b> Escrevo-lhes após a leitura atenta da excelente reportagem "O impacto das telas no desenvolvimento infantil", publicada na edição do último mês.<br><br>
        <b>[Posicionamento/Tese]</b> Gostaria de parabenizar a equipe de jornalismo pela abordagem precisa e urgente sobre a proliferação do uso precoce de smartphones entre nossas crianças. Como educadora e mãe, vivencio diariamente os desafios apontados no texto.<br><br>
        <b>[Argumentação]</b> A matéria foi extremamente feliz ao correlacionar a superexposição digital à queda na capacidade de atenção e ao aumento da ansiedade infantil. Gostaria de acrescentar que a escola também precisa ser incluída como aliada nesse processo, promovendo oficinas de conscientização para pais e responsáveis, visto que muitos entregam telas aos filhos por pura falta de alternativas de lazer ou informação.<br><br>
        <b>[Conclusão]</b> Agradeço ao veículo pelo compromisso pedagógico e social em trazer luz a temas tão vitais para a formação das futuras gerações.<br><br>
        <b>[Assinatura]</b> Mariana Souza Santos, Professora de Ensino Fundamental, Imperatriz - MA.""",
        "analise": """
        * **Objetivo:** Elogio com acréscimo de perspectiva prática.
        * **Estrutura:** Vocativo formal curto -> Referência explícita à matéria -> Elogio sincero -> Argumento complementar focado na escola -> Fechamento elegante com assinatura completa (Nome, profissão e cidade).
        """
    },
    {
        "id": 12,
        "genero": "Carta do Leitor",
        "ano": "Modelo Exemplar",
        "eixo": "🏛️ Sociedade & Cidadania",
        "tema": "Critica à matéria 'O avanço das obras do VLT na capital'",
        "texto": """<b>[Vocativo]</b> Ao Editor do Jornal O Maranhão Urgente,<br><br>
        <b>[Referência]</b> Refiro-me à matéria "O avanço das obras do VLT na capital", veiculada na capa do jornal impresso do dia 10 de outubro.<br><br>
        <b>[Posicionamento/Tese]</b> Respeito o trabalho do jornal, contudo, discordo veementemente do tom ufanista com que a reportagem tratou o progresso das obras, ignorando os severos transtornos enfrentados pelos comerciantes e moradores das vias afetadas.<br><br>
        <b>[Argumentação]</b> Há mais de seis meses, os estabelecimentos locais sofrem com a poeira, interrupção no fornecimento de água e queda brutal nas vendas, conforme relato coletivo dos pequenos empreendedores do bairro. Apresentar a obra apenas sob o prisma do benefício futuro, sem cobrar transparência do Poder Público sobre o atraso no cronograma, afasta o jornal da realidade vivida pela comunidade afetada.<br><br>
        <b>[Conclusão]</b> Espero que este renomado veículo publique esta contestação e realize uma reportagem de acompanhamento, dando voz aos cidadãos que pagam o preço do descaso diário.<br><br>
        <b>[Assinatura]</b> Carlos Eduardo Lima, Comerciante e líder comunitário, São Luís - MA.""",
        "analise": """
        * **Objetivo:** Crítica construtiva e cobrança de imparcialidade jornalística.
        * **Pontos Fortes:** Uso respeitoso e firme do tom formal; argumentação embasada em impactos econômicos reais; cobrança de uma nova pauta com escuta da comunidade.
        """
    },
    {
        "id": 13,
        "genero": "Carta do Leitor",
        "ano": "Modelo Exemplar",
        "eixo": "🌿 Meio Ambiente & Saúde",
        "tema": "Alerta sobre a poluição do Rio Tocantins após artigo de opinião",
        "texto": """<b>[Vocativo]</b> Caros Editores da Revista Meio Ambiente Hoje,<br><br>
        <b>[Referência]</b> Liquei com viva atenção o artigo de opinião "O futuro hídrico das cidades médias", publicado na edição nº 142 de sua revista.<br><br>
        <b>[Posicionamento/Tese]</b> Gostaria de manifestar minha profunda preocupação e reforçar que a situação do Rio Tocantins exige um olhar ainda mais urgente da imprensa nacional do que o retratado no artigo.<br><br>
        <b>[Argumentação]</b> Como biólogo atuante na Região Tocantina, observo diariamente os impactos do esgoto in natura e do descarte de resíduos industriais na bacia. A perda da biodiversidade aquática e o comprometimento do abastecimento de água potável não são ameaças futuras, mas uma tragédia em curso. Reportagens de alcance nacional são fundamentais para pressionar prefeituras e órgãos ambientais a aplicarem o Marco Legal do Saneamento Básico.<br><br>
        <b>[Conclusão]</b> Parabenizo a revista pela iniciativa de debater o tema e renovo o apelo para que realizem uma grande grande investigação jornalística focada nos rios do interior do Nordeste.<br><br>
        <b>[Assinatura]</b> Dr. Fernando Henrique Alencar, Biólogo e Pesquisador, Imperatriz - MA.""",
        "analise": """
        * **Objetivo:** Alerta socioambiental de urgência.
        * **Pontos Fortes:** Autoridade do remetente utilizada como argumento legítimo (biólogo); conectores formais (*Liguei com viva atenção*, *Manifestar minha profunda preocupação*).
        """
    },
    {
        "id": 14,
        "genero": "Carta do Leitor",
        "ano": "Modelo Exemplar",
        "eixo": "🎨 Cultura & Educação",
        "tema": "Proposta de complementação à matéria 'A literatura maranhense nas escolas'",
        "texto": """<b>[Vocativo]</b> Prezada Redação do Caderno de Cultura do Jornal do Estado,<br><br>
        <b>[Referência]</b> É com grande satisfação que leio a série de reportagens "A literatura maranhense nas escolas", veiculada ao longo deste mês.<br><br>
        <b>[Posicionamento/Tese]</b> Cumprimento o jornal pelo resgate da obra de clássicos como Gonçalves Dias e Aluísio Azevedo. No entanto, gostaria de sugerir uma complementação fundamental para que o quadro da nossa literatura seja completo e inclusivo.<br><br>
        <b>[Argumentação]</b> Sentimos a ausência de destaque para a obra de Maria Firmina dos Reis, primeira romancista negra do Brasil e autora de "Úrsula". Em um momento em que as escolas debatem a educação das relações étnico-raciais, dar visibilidade a essa pioneira maranhense é um dever histórico e cultural que enriquece imensamente nossos alunos.<br><br>
        <b>[Conclusão]</b> Fica aqui a sugestão de pauta para uma matéria especial sobre autoras negras da literatura maranhense. Certo de sua costumeira atenção à diversidade cultural, renovo meus cumprimentos.<br><br>
        <b>[Assinatura]</b> Professor Mestre José Ribamar Ferreira, Historiador, Caxias - MA.""",
        "analise": """
        * **Objetivo:** Sugestão de pauta e correção histórica respeitosa.
        * **Pontos Fortes:** Elogia antes de apontar a lacuna; sugere um complemento cultural de grande valor pedagógico e social (Maria Firmina dos Reis).
        """
    },
    {
        "id": 15,
        "genero": "Carta do Leitor",
        "ano": "Modelo Exemplar",
        "eixo": "🏛️ Sociedade & Cidadania",
        "tema": "Contestação à coluna de opinião sobre transporte público",
        "texto": """<b>[Vocativo]</b> Ao Conselho Editorial do Jornal Folha da Manhã,<br><br>
        <b>[Referência]</b> Dirijo-me a vocês para contestar os argumentos apresentados no artigo de opinião "A necessidade do reajuste da tarifa de ônibus", publicado em 5 de outubro.<br><br>
        <b>[Posicionamento/Tese]</b> É inaceitável defender o aumento das passagens sem exigir, em contrapartida, a melhoria mínima da frota sucateada que atende a população trabalhadora diariamente.<br><br>
        <b>[Argumentação]</b> O articulista justifica o reajuste com base na inflação dos combustíveis, mas omite a realidade dos passageiros: veículos lotados, quebras frequentes e falta de acessibilidade para pessoas com deficiência. O transporte público é um direito social garantido pelo Artigo 6º da Constituição Federal e não pode ser tratado como mero negócio lucrativo que penaliza quem ganha menos.<br><br>
        <b>[Conclusão]</b> Solicito a publicação desta carta no espaço reservado ao leitor em respeito ao contraditório e à pluralidade de vozes que um jornalismo ético deve assegurar.<br><br>
        <b>[Assinatura]</b> Ana Beatriz Prado, Estudante Universitária e Usuária do Transporte Público, Imperatriz - MA.""",
        "analise": """
        * **Objetivo:** Contestação e defesa de direitos sociais.
        * **Pontos Fortes:** Uso de repertório jurídico (Artigo 6º da Constituição); tom indignado, porém extremamente respeitoso e ancorado na técnica do gênero.
        """
    },

    # ------------------ REDAÇÕES DISSERTATIVAS ------------------
    {
        "id": 1,
        "genero": "Redação UEMASUL",
        "ano": "PAES / UEMASUL",
        "eixo": "🏛️ Sociedade & Cidadania",
        "tema": "O papel da juventude na transformação social e política no Maranhão",
        "texto": """<b>[Título]</b> Os Jovens e o Protagonismo Transformador<br><br>
        <b>[Introdução]</b> A história das transformações sociais sempre contou com a energia e o questionamento das novas gerações. No contexto contemporâneo do Maranhão, o papel do jovem ultrapassa a mera expectativa de futuro e consolida-se como força ativa no presente. Nesse cenário, o protagonismo juvenil é indispensável para promover a justiça social e superar desigualdades históricas.<br><br>
        <b>[Desenvolvimento 1]</b> Em primeiro lugar, cumpre destacar que a participação política dos jovens vai muito além do voto formal. Inspirados pelo conceito de ação comunicativa de Jürgen Habermas, os movimentos estudantis e comunitários utilizam o debate como ferramenta de conscientização. Quando a juventude ocupa espaços de discussão, fomenta-se uma cidadania crítica capaz de cobrar políticas públicas para a educação e a preservação da identidade cultural local.<br><br>
        <b>[Desenvolvimento 2]</b> Além disso, a tecnologia surge como uma grande aliada no engajamento social juvenil. Em uma sociedade cada vez mais conectada, as redes sociais tornam-se praças públicas virtuais onde projetos comunitários ganham visibilidade e mobilização rápida. Contudo, essa atuação digital precisa ser acompanhada de ações concretas nas periferias e cidades do interior, garantindo que o conhecimento se converta em melhoria real na vida da população.<br><br>
        <b>[Conclusão]</b> Em suma, o protagonismo da juventude é o motor indispensável para o desenvolvimento do Estado. Cabe às instituições de ensino e ao poder público abrir caminhos para que as vozes jovens sejam ouvidas e integradas na tomada de decisões. Somente assim o Maranhão avançará rumo a uma sociedade mais equitativa, onde a juventude não seja vista como mera promessa, mas como agente de mudança efetiva.""",
        "analise": """
        * **Particularidades UEMASUL/PAES:** Título obrigatório presente e atrativo; foco na argumentação crítica sem exigência dos 5 elementos do ENEM; nota final 10,0.
        * **Repertório:** Jürgen Habermas (Ação comunicativa) e análise do engajamento juvenil socio-histórico regional.
        """
    },
    {
        "id": 2,
        "genero": "Redação ENEM",
        "ano": "ENEM 2021",
        "eixo": "🏛️ Sociedade & Cidadania",
        "tema": "Invisibilidade e registro civil: garantia de acesso à cidadania no Brasil",
        "texto": """<b>[Introdução]</b> Na obra "Vidas Secas", do escritor modernista Graciliano Ramos, a família de Fabiano vive em uma condição de vulnerabilidade extrema e ausência de direitos básicos. Fora da ficção, a realidade de milhões de brasileiros reflete a mesma precariedade descrita no livro, uma vez que a falta do registro civil impede que esses indivíduos acessem a cidadania plena. Nesse contexto, a invisibilidade promovida pela ausência de documentos decorre tanto do descaso governamental quanto da desinformação da sociedade.<br><br>
        <b>[Desenvolvimento 1]</b> Em primeiro lugar, vale ressaltar que a negligência do Estado é um fator determinante para a manutenção do problema. Segundo o filósofo Thomas Hobbes, o Estado é responsável por garantir o bem-estar e a segurança dos cidadãos. Contudo, a burocracia excessiva e a escassez de postos de atendimento para a emissão da certidão de nascimento nas áreas periféricas e rurais contradizem o dever estatal. Como consequência, a ausência de registro priva o cidadão de programas sociais e de direitos fundamentais.<br><br>
        <b>[Desenvolvimento 2]</b> Ademais, a falta de informação atua como catalisadora dessa marginalização. Para a socióloga Lilia Schwarcz, o Brasil construiu estruturas de exclusão que perpetuam a desigualdade social. Nesse prisma, grande parte da população vulnerável desconhece a gratuidade da primeira via da certidão de nascimento garantida por lei. Assim, por falta de conhecimento, muitas famílias permanecem sem documentação oficial, reproduzindo um ciclo de invisibilidade ao longo de gerações.<br><br>
        <b>[Conclusão]</b> Portanto, medidas urgentes são necessárias para combater a invisibilidade gerada pela falta de registro civil. Para tanto, cabe ao Ministério da Mulher, da Família e dos Direitos Humanos, em parceria com as prefeituras municipais, promover mutirões itinerantes para a emissão gratuita de documentos básicos nas comunidades mais isoladas. Essa ação deve ser realizada por meio de veículos adaptados com equipes de cartório e assistentes sociais, a fim de garantir que a certidão alcance toda a população vulnerável. Com essas ações, o Brasil poderá assegurar a cidadania plena e afastar a realidade vivenciada em "Vidas Secas".""",
        "analise": """
        * **Repertórios:** *Vidas Secas* (Graciliano Ramos), Thomas Hobbes (Contratualismo) e Lilia Schwarcz.
        * **Análise C5:** Agente (*Ministério + Prefeituras*), Ação (*mutirões itinerantes*), Meio (*veículos adaptados*), Detalhamento (*com cartórios e assistentes*) e Efeito (*assegurar cidadania plena*).
        """
    },
    {
        "id": 3,
        "genero": "Redação ENEM",
        "ano": "ENEM 2018",
        "eixo": "💻 Tecnologia & Comunicação",
        "tema": "Manipulação do comportamento do usuário pelo controle de dados na internet",
        "texto": """<b>[Introdução]</b> Em sua obra "1984", George Orwell retrata uma sociedade distópica na qual o Estado exerce um controle absoluto sobre os pensamentos e ações dos indivíduos. Análogo à ficção, o uso de dados de navegação na internet contemporânea tem permitido a manipulação do comportamento dos usuários, ferindo a autonomia individual. Isso ocorre devido à busca desenfreada por lucro pelas empresas de tecnologia e à falta de letramento digital da população.<br><br>
        <b>[Desenvolvimento 1]</b> Em primeira análise, cabe destacar que a mercantilização de informações pessoais é um motor desse cenário. Conforme o filósofo Zygmunt Bauman, no contexto da modernidade líquida, as relações econômicas sobrepõem-se aos valores éticos. Nessa ótica, algoritmos organizam bolhas informacionais para direcionar conteúdos comerciais e ideológicos, condicionando as escolhas do consumidor sem que este perceba.<br><br>
        <b>[Desenvolvimento 2]</b> Além disso, a passividade dos internautas intensifica essa vulnerabilidade. O conceito de "Menoridade", formulado por Immanuel Kant, refere-se à incapacidade do indivíduo de pensar por si mesmo sem a condução de outro. De forma análoga, a falta de educação digital faz com que grande parte dos usuários aceite de maneira acrítica os conteúdos recomendados pelas plataformas virtuais, tornando-se presa fácil da manipulação de dados.<br><br>
        <b>[Conclusão]</b> Infere-se, portanto, a urgência de mitigar o controle de dados na internet. Para isso, o Ministério da Educação, aliado ao Ministério das Comunicações, deve implementar oficinas de educação digital nas escolas públicas e privadas. Essa medida será executada por meio de aulas práticas de tecnologia e palestras com especialistas em segurança cibernética, visando formar cidadãos críticos e capazes de navegar com autonomia na rede.""",
        "analise": """
        * **Repertórios:** *1984* (Orwell), Zygmunt Bauman (Modernidade Líquida) e Immanuel Kant (Menoridade Intelectual).
        """
    },
    {
        "id": 4,
        "genero": "Redação ENEM",
        "ano": "ENEM 2019",
        "eixo": "🎨 Cultura & Educação",
        "tema": "Democratização do acesso ao cinema no Brasil",
        "texto": """<b>[Introdução]</b> Na obra "Utopia", do escritor inglês Thomas More, é retratada uma sociedade perfeita na qual todos os indivíduos têm acesso igualitário aos direitos e ao bem-estar. No entanto, ao analisar o acesso ao cinema no Brasil, percebe-se que a realidade dista do ideal utópico, haja vista que a democratização desse recurso cultural ainda é incipiente. Essa problemática é alimentada tanto pelo elitismo socioeconômico do setor quanto pela concentração geográfica das salas de exibição.<br><br>
        <b>[Desenvolvimento 1]</b> Sob essa ótica, cabe pontuar que o alto custo dos ingressos inviabiliza o acesso das camadas populares à arte cinematográfica. O sociólogo Pierre Bourdieu cunhou o conceito de "Capital Cultural" para explicar como o consumo de bens artísticos é utilizado como marca de distinção social. Nesse sentido, os altos preços cobrados pelas redes de cinema transformam a sétima arte em um privilégio das elites, excluindo os cidadãos de menor renda.<br><br>
        <b>[Desenvolvimento 2]</b> Além disso, a distribuição desigual dos complexos de cinema reforça esse cenário de exclusão. De acordo com o geógrafo Milton Santos, a cidadania se realiza plenamente no território, de modo que a falta de infraestrutura nas periferias limita o exercício dos direitos dos cidadãos. Contudo, a maioria das salas de cinema no Brasil está concentrada nos shoppings de bairros nobres dos grandes centros urbanos.<br><br>
        <b>[Conclusão]</b> Depreende-se, pois, a necessidade de democratizar o acesso ao cinema no país. Para isso, o Ministério da Cultura deve, por meio do redirecionamento de verbas e parcerias com o setor privado, subsidiar o preço dos ingressos para estudantes de escolas públicas e construir salas populares em periferias e cidades do interior. Espera-se, com isso, aproximar o Brasil da sociedade justa e democrática idealizada por Thomas More.""",
        "analise": """
        * **Repertórios:** Thomas More (*Utopia*), Pierre Bourdieu (*Capital Cultural*) e Milton Santos (*Cidadania e Território*).
        """
    },
    {
        "id": 5,
        "genero": "Redação ENEM",
        "ano": "ENEM 2020",
        "eixo": "🌿 Meio Ambiente & Saúde",
        "tema": "O estigma associado às doenças mentais na sociedade brasileira",
        "texto": """<b>[Introdução]</b> Na obra "O Alienista", de Machado de Assis, o médico Simão Bacamarte interna grande parte da população sob o pretexto de tratar transtornos mentais, evidenciando o preconceito em torno da loucura. Fora da literatura, o estigma associado às doenças mentais ainda persiste na sociedade brasileira contemporânea. Esse quadro alarmante é mantido tanto pelo tabu cultural em torno da saúde mental quanto pela insuficiência da rede pública de apoio psicológico.<br><br>
        <b>[Desenvolvimento 1]</b> Em primeiro lugar, cumpre analisar como o preconceito enraizado dificulta a busca por tratamento. De acordo com o filósofo Michel Foucault em "História da Loucura", a sociedade tende a isolar e rotular aquilo que foge aos padrões tradicionais de produtividade. Sob essa lógica, indivíduos afetados pela depressão ou ansiedade são frequentemente taxados de 'fracos', o que gera silenciamento e agrava o sofrimento psíquico.<br><br>
        <b>[Desenvolvimento 2]</b> Ademais, a precariedade dos serviços públicos de saúde mental consolida essa problemática. Segundo a Constituição Federal de 1988, a saúde é um direito de todos e dever do Estado. Todavia, a escassez de profissionais e a sobrecarga dos Centros de Atenção Psicossocial (CAPS) deixam milhares de pessoas sem acompanhamento, violando a prerrogativa constitucional.<br><br>
        <b>[Conclusão]</b> Portanto, medidas são urgentes para desconstruir o estigma sobre os transtornos mentais no Brasil. Para tanto, cabe ao Ministério da Saúde ampliar o investimento na rede de CAPS, contratando mais psicólogos e psiquiatras por meio de concursos públicos. Paralelamente, o Ministério da Educação deve promover campanhas educativas nas escolas com palestras abertas à comunidade, a fim de conscientizar a população e erradicar o preconceito.""",
        "analise": """
        * **Repertórios:** *O Alienista* (Machado de Assis), Michel Foucault (*História da Loucura*) e Constituição Federal de 1988.
        """
    }
]

# --- GERENCIAMENTO DE SESSÕES ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {
        "ENEM: Redação 1": {
            "tipo": "ENEM",
            "frases_aluno": [],
            "avaliacao_guardada": "",
            "mensagens": [{"role": "assistant", "content": "Fala, futuro nota 1000! 🎓 Sou seu professor e parceiro de treino aqui na Oficina.\n\nPara a gente começar com o pé direito, **qual é o tema da redação** que você quer mandar ver hoje?"}]
        }
    }
    st.session_state.current_session = "ENEM: Redação 1"

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### 🧑‍🏫 **Oficina de Redação**")
    st.caption("Seu espaço prático de escrita")

    genero_escolhido = st.selectbox(
        "🎯 O que vamos treinar?",
        ["Redação ENEM", "Redação UEMASUL (PAES)", "Carta do Leitor"]
    )

    if st.button("✨ Iniciar Nova Prática", use_container_width=True, type="primary"):
        num = len(st.session_state.sessions) + 1
        if genero_escolhido == "Redação ENEM":
            nova_chave = f"ENEM: Treino {num}"
            msg_inicial = "Fala, futuro nota 1000! 🎓 Pronto para mais um treino do ENEM?\n\nQual é o **tema** da redação que vamos trabalhar hoje?"
            tipo = "ENEM"
        elif genero_escolhido == "Redação UEMASUL (PAES)":
            nova_chave = f"UEMASUL: Treino {num}"
            msg_inicial = "Excelente escolha! 🏛️ A redação do PAES/UEMASUL vale **10,0 pontos** e exige um **Título Criativo** obrigatório!\n\nPara começarmos, qual é o **tema** do PAES que você quer treinar?"
            tipo = "UEMASUL"
        else:
            nova_chave = f"Carta: Treino {num}"
            msg_inicial = "Excelente escolha! ✉️ A Carta do Leitor é um gênero incrível para defender sua voz na imprensa.\n\nPara começarmos, qual é a **notícia, reportagem ou tema** que motivou a sua carta?"
            tipo = "CARTA"

        st.session_state.sessions[nova_chave] = {
            "tipo": tipo,
            "frases_aluno": [],
            "avaliacao_guardada": "",
            "mensagens": [{"role": "assistant", "content": msg_inicial}]
        }
        st.session_state.current_session = nova_chave
        st.rerun()

    lista_sessoes = list(st.session_state.sessions.keys())
    sessao_selecionada = st.selectbox(
        "🗂️ Suas Práticas Salvas:",
        lista_sessoes,
        index=lista_sessoes.index(st.session_state.current_session)
    )

    if sessao_selecionada != st.session_state.current_session:
        st.session_state.current_session = sessao_selecionada
        st.rerun()

    st.divider()

    # --- CRONÔMETRO DE PROVA ---
    st.markdown("### ⏱️ **Simulador de Tempo de Prova**")
    tempo_opcao = st.selectbox("Escolha o tempo do treino:", ["Sem cronômetro", "30 minutos", "60 minutos", "90 minutos"])
    
    if tempo_opcao != "Sem cronômetro":
        minutos = int(tempo_opcao.split()[0])
        if "timer_start" not in st.session_state or st.button("🔄 Iniciar/Resetar Timer"):
            st.session_state.timer_start = time.time()
            st.session_state.timer_duration = minutos * 60

        tempo_decorrido = time.time() - st.session_state.get("timer_start", time.time())
        tempo_restante = max(0, st.session_state.get("timer_duration", 0) - tempo_decorrido)
        
        mins, secs = divmod(int(tempo_restante), 60)
        st.markdown(f"<div class='timer-box'>⏳ Tempo Restante: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
        if tempo_restante == 0:
            st.warning("⚠️ O tempo do seu simulado terminou! Finalize seu texto e solicite a avaliação.")

    st.divider()

    # GUIAS ESTRUTURAIS
    tipo_atual = st.session_state.sessions[st.session_state.current_session]["tipo"]

    if tipo_atual == "ENEM":
        st.markdown("### 🧭 **Guia Rápido ENEM**")
        with st.expander("1️⃣ Introdução"):
            st.markdown("* **F1:** Contextualização.\n* **F2:** Ponte com o Tema.\n* **F3:** Tese + Argumentos D1 e D2.")
        with st.expander("2️⃣ Desenvolvimento (D1 e D2)"):
            st.markdown("* **F1:** Tópico Frasal.\n* **F2:** Repertório.\n* **F3:** Análise Crítica.\n* **F4:** Fechamento.")
        with st.expander("3️⃣ Conclusão"):
            st.markdown("* **F1:** Retomada da tese.\n* **F2:** Proposta (Agente, Ação, Meio, Detalhe e Efeito).")

    elif tipo_atual == "UEMASUL":
        st.markdown("### 🧭 **Guia PAES / UEMASUL (Nota 10)**")
        with st.expander("📌 Regras de Ouro PAES", expanded=True):
            st.markdown("""
            * **Escala de Nota:** Vale de **0,0 a 10,0**.
            * **Título:** **OBRIGATÓRIO!** Deve ser criativo e alinhado ao tema.
            * **Foco:** Defesa crítica de ponto de vista e coerência.
            * **Conclusão:** Síntese reflexiva sem detalhamento do ENEM.
            """)
        with st.expander("1️⃣ Título + Introdução"):
            st.markdown("* **Título:** Criativo e alinhado.\n* **F1:** Contexto.\n* **F2:** Tese clara.")
        with st.expander("2️⃣ Desenvolvimento"):
            st.markdown("* Argumentação sólida com fatos e reflexão social.")
        with st.expander("3️⃣ Conclusão"):
            st.markdown("* Fechamento reflexivo reafirmando a tese.")

    else:
        st.markdown("### 🧭 **Guia: Carta do Leitor**")
        with st.expander("📖 Entenda o Gênero", expanded=True):
            st.markdown("Espaço de diálogo com jornais/revistas para elogiar, criticar ou enriquecer um debate público.")
        with st.expander("1️⃣ Vocativo & Início"):
            st.markdown("* **Vocativo:** Cumprimento formal.\n* **Referência:** Menção à matéria base.")
        with st.expander("2️⃣ Sua Posição & Argumentos"):
            st.markdown("* Opinião clara sustentada por fatos e reflexões.")
        with st.expander("3️⃣ Fechamento & Assinatura"):
            st.markdown("* Síntese da intenção + Nome/Cidade.")

# --- TELA PRINCIPAL ---
st.markdown("<h1 class='main-title'>🎓 Oficina de Redação Passo a Passo</h1>", unsafe_allow_html=True)

aba_pratica, aba_biblioteca = st.tabs(["✍️ **Oficina de Escrita (Chat)**", "📚 **Biblioteca de Modelos de Excelência**"])

# ==============================================================================
# ABA 1: OFICINA DE ESCRITA, AVALIAÇÃO E EXPORTAÇÃO
# ==============================================================================
with aba_pratica:
    st.caption(f"📌 Prática Ativa: **{st.session_state.current_session}**")

    dados_sessao = st.session_state.sessions[st.session_state.current_session]
    mensagens_atuais = dados_sessao["mensagens"]

    if "frases_aluno" not in dados_sessao:
        dados_sessao["frases_aluno"] = []
    if "avaliacao_guardada" not in dados_sessao:
        dados_sessao["avaliacao_guardada"] = ""

    # --- PAINEL DO TEXTO EM CONSTRUÇÃO & EXPORTAÇÃO ---
    with st.expander("📄 **Seu Texto em Construção & Exportação**", expanded=False):
        if len(dados_sessao["frases_aluno"]) > 1:
            texto_completo = " ".join(dados_sessao["frases_aluno"][1:])
            st.markdown(f"<div class='texto-consolidado'>{texto_completo}</div>", unsafe_allow_html=True)
            
            col_eval, col_down = st.columns([2, 1])
            
            btn_label = "📊 Avaliar Redação PAES (0 a 10)" if tipo_atual == "UEMASUL" else "📊 Avaliar Texto (Atribuir Nota)"
            with col_eval:
                if st.button(btn_label, type="primary"):
                    with st.spinner("O professor está analisando seu texto..."):
                        client = genai.Client()
                        
                        if tipo_atual == "UEMASUL":
                            prompt_avaliacao = f"""
                            Atue como um corretor oficial da banca UEMASUL / PAES.
                            Analise a redação abaixo e atribua uma NOTA FINAL DE 0,0 A 10,0 PONTOS.

                            REDAÇÃO DO ALUNO:
                            "{texto_completo}"

                            Formate obrigatoriamente nesta estrutura:
                            ### 📊 Ficha de Avaliação PAES / UEMASUL
                            * **Título:** [Presente/Ausente]
                            * **Domínio do Gênero Dissertativo:** [Nota/2.5]
                            * **Desenvolvimento e Argumentação:** [Nota/2.5]
                            * **Coesão e Estrutura Textual:** [Nota/2.5]
                            * **Norma Culta e Gramática:** [Nota/2.5]

                            **🎯 NOTA FINAL PAES:** [Soma total de 0,0 a 10,0]

                            **💡 Dicas de Ouro para o Próximo Treino UEMASUL:**
                            (2 a 3 pontos práticos de melhoria)
                            """
                        else:
                            prompt_avaliacao = f"""
                            Atue como corretor oficial do ENEM.
                            Analise a redação e forneça nota de 0 a 1000 por competência (C1 a C5).

                            REDAÇÃO DO ALUNO:
                            "{texto_completo}"

                            Formate com C1 a C5 (200 pts cada), NOTA FINAL /1000 e Dicas de Ouro.
                            """

                        try:
                            avaliacao_res = client.models.generate_content(
                                model="gemini-3.8-flash",
                                contents=prompt_avaliacao
                            )
                            dados_sessao["avaliacao_guardada"] = avaliacao_res.text
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao gerar avaliação: {e}")

            if dados_sessao["avaliacao_guardada"]:
                st.markdown(dados_sessao["avaliacao_guardada"])
                
                conteudo_download = f"""==================================================
OFICINA DE REDAÇÃO - FICHA DE PRÁTICA E AVALIAÇÃO
Data: {datetime.date.today().strftime('%d/%m/%Y')}
Sessão: {st.session_state.current_session}
==================================================

[TEXTO PRODUZIDO]
{texto_completo}

==================================================
[AVALIAÇÃO DO PROFESSOR]
{dados_sessao['avaliacao_guardada']}
==================================================
"""
                with col_down:
                    st.download_button(
                        label="📥 Baixar Texto (TXT)",
                        data=conteudo_download,
                        file_name=f"Texto_{st.session_state.current_session.replace(':', '_').replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
        else:
            st.info("Seu texto aparecerá escrito por extenso aqui conforme você for enviando as frases ao professor!")

    st.divider()

    if tipo_atual == "ENEM":
        SYSTEM_INSTRUCTION = """
        Você é um professor parceiro, didático e motivador de redação para o ENEM.
        Seu estilo de comunicação é acolhedor, positivo, direto e humano (nunca robótico).
        Regras pedagógicas:
        1. Acompanhe a escrita do aluno FRASE POR FRASE. Nunca escreva o texto por ele.
        2. Antes de pedir a próxima frase, dê uma dica rápida e clara do objetivo dela.
        3. Quando a frase do aluno for boa, elogie com entusiasmo!
        """
    elif tipo_atual == "UEMASUL":
        SYSTEM_INSTRUCTION = """
        Você é um professor parceiro especialista na banca do PAES / UEMASUL.
        Seu estilo de comunicação é encorajador, didático e focado nos critérios da UEMASUL.
        Regras pedagógicas:
        1. Acompanhe a escrita do aluno FRASE POR FRASE. Nunca escreva o texto por ele.
        2. PASSO 1 OBRIGATÓRIO: O aluno deve definir o TÍTULO da redação logo após o tema.
        3. Após o título, guie a estrutura dissertativa parágrafo a parágrafo.
        """
    else:
        SYSTEM_INSTRUCTION = """
        Você é um professor dinâmico especialista no gênero Carta do Leitor.
        Seu estilo de comunicação é motivador, amigável e focado em clareza textual.
        Regras pedagógicas:
        1. Oriente a construção da Carta parte por parte. Nunca escreva a carta por ele.
        2. Explique a função de cada bloco da carta antes de solicitar que o aluno escreva.
        """

    for msg in mensagens_atuais:
        avatar = "🧑‍🏫" if msg["role"] == "assistant" else "✍️"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    if prompt := st.chat_input("Escreva sua frase, título ou resposta aqui..."):
        mensagens_atuais.append({"role": "user", "content": prompt})
        dados_sessao["frases_aluno"].append(prompt)
        
        with st.chat_message("user", avatar="✍️"):
            st.write(prompt)

        with st.chat_message("assistant", avatar="🧑‍🏫"):
            with st.spinner("O professor está lendo sua frase..."):
                client = genai.Client()

                formatted_history = []
                for msg in mensagens_atuais[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    formatted_history.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=msg["content"])]
                        )
                    )

                chat = client.chats.create(
                    model="gemini-3.8-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.4
                    ),
                    history=formatted_history
                )

                max_tentativas = 3
                for tentativa in range(max_tentativas):
                    try:
                        resposta = chat.send_message(prompt)
                        st.write(resposta.text)
                        mensagens_atuais.append({"role": "assistant", "content": resposta.text})
                        break
                    except APIError as e:
                        if e.code == 503 and tentativa < max_tentativas - 1:
                            time.sleep(2)
                            continue
                        else:
                            st.error("Ops! Tive um pequeno imprevisto com a conexão aqui. Pode reenviar a frase em alguns segundos?")
                            break
                    except Exception as e:
                        st.error(f"Ocorreu um detalhe técnico: {e}")
                        break

# ==============================================================================
# ABA 2: BIBLIOTECA DINÂMICA DE MODELOS (REDAÇÕES + CARTAS DO LEITOR)
# ==============================================================================
with aba_biblioteca:
    st.markdown("## 📚 **Biblioteca de Modelos de Excelência**")
    st.caption("Estude com exemplares de Redações Nota 1000 (ENEM), Redações Nota 10,0 (PAES/UEMASUL) e Cartas do Leitor comentadas passo a passo.")

    col_filtro1, col_filtro2 = st.columns([1, 1])

    with col_filtro1:
        genero_filtro = st.selectbox(
            "📂 **Filtrar por Gênero/Banca:**",
            ["Todos os Gêneros", "Redação ENEM", "Redação UEMASUL", "Carta do Leitor"]
        )

    with col_filtro2:
        eixo_filtro = st.selectbox(
            "🔎 **Filtrar por Eixo Temático:**",
            ["Todos os Eixos", "🏛️ Sociedade & Cidadania", "💻 Tecnologia & Comunicação", "🎨 Cultura & Educação", "🌿 Meio Ambiente & Saúde"]
        )

    # Lógica de Filtragem dupla
    lista_exibicao = REDACOES_NOTA_1000

    if genero_filtro != "Todos os Gêneros":
        lista_exibicao = [item for item in lista_exibicao if item.get("genero", "Redação ENEM") == genero_filtro or (genero_filtro == "Redação UEMASUL" and item.get("ano") == "PAES / UEMASUL")]

    if eixo_filtro != "Todos os Eixos":
        lista_exibicao = [item for item in lista_exibicao if item["eixo"] == eixo_filtro]

    st.markdown(f"Exibindo **{len(lista_exibicao)}** exemplo(s) no acervo:")

    for item in lista_exibicao:
        estilo_card = "card-carta" if item.get("genero") == "Carta do Leitor" else "card-nota1000"
        tag_genero = f"✉️ {item.get('genero', 'Redação')}" if item.get("genero") == "Carta do Leitor" else f"🏆 {item.get('ano', 'Nota Máxima')}"

        with st.expander(f"{tag_genero} | **{item['eixo']}** - *{item['tema']}*"):
            st.markdown(f"<div class='{estilo_card}'>{item['texto']}</div>", unsafe_allow_html=True)
            st.markdown("#### 🔍 **Análise Anatômica do Texto:**")
            st.markdown(item["analise"])
