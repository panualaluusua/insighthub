# Käyttäjäprofiili ja Palautemekanismin Toteutus (Tehtävät #6 & #12)

## Strateginen Konteksti ja Tavoitteet

Tämä dokumentti on tekninen toteutussuunnitelma yhdelle InsightHubin keskeisimmistä kilpailueduista: **syvälle personoinnille**. Se vastaa suoraan `INSIGHTHUB_STRATEGIC_POSITIONING.md`-dokumentissa määriteltyihin tavoitteisiin, erityisesti **Pilari 2: Syvä Personointi** ja **Aloite 2: Systematisoi Semanttisen Relevanssin Palaute**.

Tässä kuvatut mekanismit – dynaaminen `interest_vector` ja rakeinen palautejärjestelmä – ovat välttämättömiä `ContentScorer`-solmulle, joka on määritelty `ARCHITECTURE.md`-dokumentissa. Ne muodostavat oppivan järjestelmän, joka mahdollistaa poikkeuksellisen relevanssin ja toteuttaa projektin ydinlupauksen "henkilökohtaisena tekoälyanalyytikkona".

Tämä suunnitelma kattaa **Tehtävät #6 (Käyttäjäprofiilit)** ja **#12 (Oppiminen palautteesta)**.

## Sisällysluettelo
- [Strateginen Konteksti ja Tavoitteet](#strateginen-konteksti-ja-tavoitteet)
- [Osa I: Keskusteleva Perehdytys ja Alkuprofiilin Luonti](#osa-i-keskusteleva-perehdytys-ja-alkuprofiilin-luonti)
- [Osa II: Matemaattinen Malli Profiilin Kehittymiselle](#osa-ii-matemaattinen-malli-profiilin-kehittymiselle)
- [Osa III: Systematisoitu Palautesilmukan Toteutus](#osa-iii-systematisoitu-palautesilmukan-toteutus)

---

## Osa I: Keskusteleva Perehdytys ja Alkuprofiilin Luonti

Tässä osassa kuvataan yksityiskohtaisesti kielimallipohjaisen (LLM) perehdytysketjun suunnittelu ja toteutus. Arkkitehtuuriseksi valinnaksi on tehty LangChain Expression Language (LCEL), joka on moderni ja deklaratiivinen viitekehys tekoälylogiikan koostamiseen.

### 1.1 Arkkitehtoninen Lähestymistapa: LangChain Expression Language (LCEL)

Järjestelmän toteutuksessa hyödynnetään yksinomaan LangChain Expression Language (LCEL) -kieltä. Tämä valinta perustuu LCEL:n tarjoamiin merkittäviin etuihin:
- **Seurattavuus (Observability):** Saumaton LangSmith-jäljitys.
- **Suorituskyky:** Optimoitu rinnakkaisen ja asynkronisen prosessoinnin avulla.
- **Intuitiivinen Syntaksi:** Koostettava logiikka putkioperaattorilla (`|`).

Perehdytysprosessi on yhtenäinen LCEL-ketju, joka koostuu kahdesta päävaiheesta:
1.  **Alustava Kiinnostuksen Kohteiden Ekstrahointi:** Jäsentää käyttäjän vapaamuotoisen esittelytekstin.
2.  **Dialogipohjainen Tarkennus:** Luo tarkentavia kysymyksiä syventääkseen profiilia.

### 1.2 Vaihe 1: Kiinnostuksen Kohteiden Ekstrahointi

Ensimmäinen ketju jäsentää käyttäjän syötteen ja muuntaa sen strukturoituun `UserInterests`-muotoon Pydantic-skeeman avulla.

**Koodiesimerkki: Ekstraktioketju**
```python
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# 1. Pydantic-skeeman määrittely strukturoidulle datalle
class UserInterests(BaseModel):
    """Strukturoitu data, joka kuvaa käyttäjän kiinnostuksen kohteita."""
    topics: List[str] = Field(description="Lista keskeisistä aiheista tai konsepteista, jotka käyttäjä mainitsi.")
    entities: Optional[List[str]] = Field(description="Lista nimetyistä entiteeteistä, kuten yrityksistä, teknologioista tai henkilöistä.")
    overall_summary: str = Field(description="Yhden lauseen tiivistelmä käyttäjän pääasiallisista kiinnostuksen kohteista.")

# 2. Kielimallin alustus
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 3. Ekstraktioketjun luonti LCEL:llä
structured_llm = llm.with_structured_output(UserInterests)

# 4. Prompt-mallin määrittely
extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", "Olet asiantuntija, joka osaa poimia strukturoitua tietoa tekstistä. Käyttäjä kuvailee kiinnostuksen kohteitaan. Parsi tekstistä avainaiheet, entiteetit ja luo lyhyt yhteenveto."),
    ("human", "{user_text}")
])

# Koko ketju: prompt -> strukturoitu LLM
extraction_chain = extraction_prompt | structured_llm

# Esimerkkisuoritus
user_description = "Olen todella kiinnostunut tekoälyn soveltamisesta rahoitusalalla, erityisesti algoritmisesta kaupankäynnistä ja riskienhallinnasta. Seuraan aktiivisesti Nvidian ja Googlen kehitystä tällä saralla. Myös syväoppimisen teoreettiset perusteet kiehtovat minua."
extracted_data = extraction_chain.invoke({"user_text": user_description})

print("Ekstraktoitu data:")
print(extracted_data)
```

### 1.3 Vaihe 2: Tarkentavien Kysymysten Generointi

Toinen LCEL-ketju ottaa `UserInterests`-objektin syötteekseen ja generoi 2-3 avointa kysymystä, jotka syventävät ymmärrystä käyttäjän profiilista. `MessagesPlaceholder` mahdollistaa monivuoroisen keskustelun.

**Koodiesimerkki: Kysymysten Generointiketju**
```python
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder

# Prompt-malli kysymysten generointiin
question_generation_prompt = ChatPromptTemplate.from_messages([
    ("system", "Olet asiantuntijahaastattelija. Tehtäväsi on syventää ymmärrystä käyttäjän kiinnostuksen kohteista. Perustuen annettuun yhteenvetoon, aiheisiin ja entiteetteihin, esitä 2-3 oivaltavaa, avointa kysymystä. Älä toista annettuja tietoja, vaan kysy tarkennuksia tai esimerkkejä."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "Annetut tiedot:
Aiheet: {topics}
Entiteetit: {entities}
Tiivistelmä: {summary}

{user_input}")
])

# Kysymysten generointiketju
question_generation_chain = question_generation_prompt | llm

# Ensimmäinen kysymyskierros
initial_questions_response = question_generation_chain.invoke({
    "topics": extracted_data.topics,
    "entities": extracted_data.entities,
    "summary": extracted_data.overall_summary,
    "chat_history": [],
    "user_input": "Generoi ensimmäiset kysymykset tämän perusteella."
})

print("\nGeneroidut tarkentavat kysymykset:")
print(initial_questions_response.content)
```

### 1.4 Dialogin Konsolidointi ja Vektorointi

Lopuksi koko keskustelu (alkuperäinen teksti + dialogi) yhdistetään yhdeksi dokumentiksi. Tämä dokumentti syötetään upotusmallille (esim. Sentence-Transformers) luoden `interest_vector`. Vektori tallennetaan Supabasen `profiles`-tauluun ja liitetään käyttäjän `user_id`:hen.

---

## Osa II: Matemaattinen Malli Profiilin Kehittymiselle

Tämä osa esittää matemaattisen perustan `interest_vector`-vektorin inkrementaaliselle päivittämiselle käyttäjän vuorovaikutusten perusteella.

### 2.1 Vektorin Ydinpäivityskaava

Päivitys tapahtuu seuraavalla kaavalla:

$$ \vec{v}_{\text{new}} = \text{normalize}(\vec{v}_{\text{old}} + (w \cdot \vec{v}_{\text{content}})) $$

- **$\vec{v}_{\text{old}}$**: Käyttäjän nykyinen `interest_vector`.
- **$\vec{v}_{\text{content}}$**: Vuorovaikutuksen kohteena olleen sisällön upotusvektori.
- **$w$**: Skalaaripaino, joka määrittää palautteen suunnan ja voimakkuuden.

### 2.2 Painoarvojen (`w`) Määrittely

Painoarvo `w` on dynaaminen ja riippuu palautteen tyypistä:

| Palautetyyppi | `w` (Painoarvo) | Kuvaus |
| :--- | :--- | :--- |
| **Tykkäys / Positiivinen** | `+0.10` | Vahvistaa kiinnostusta. |
| **Piilotus / Negatiivinen** | `-0.15` | Vähentää relevanssia voimakkaammin. |
| **Rakeinen (esim. "liian pinnallinen")** | `-0.05` - `+0.05` | Hienovaraisempi, suunnattu päivitys. |

### 2.3 Koodiesimerkki: Vektoripäivitys

Funktio päivittää ja normalisoi käyttäjän profiilivektorin.

```python
import numpy as np

def update_and_normalize_vector(
    old_vector: np.ndarray,
    content_vector: np.ndarray,
    weight: float
) -> np.ndarray:
    """
Päivittää käyttäjän kiinnostusvektorin, käsittelee nollavektorin ja normalisoi tuloksen.
    """
    new_vector = np.asarray(old_vector, dtype=np.float32) + (weight * np.asarray(content_vector, dtype=np.float32))
    norm = np.linalg.norm(new_vector)
    if norm == 0:
        return new_vector
    return new_vector / norm

# Esimerkkikäyttö
user_profile_vector = np.array([0.1, 0.9, 0.2, 0.0, 0.1])
user_profile_vector /= np.linalg.norm(user_profile_vector)

content_vector_liked = np.array([0.2, 0.8, 0.3, 0.1, 0.0])
content_vector_liked /= np.linalg.norm(content_vector_liked)

# Käyttäjä tykkää sisällöstä (positiivinen päivitys)
updated_vector = update_and_normalize_vector(user_profile_vector, content_vector_liked, 0.10)
print("Päivitetty vektori (tykkäys):", updated_vector)
```

---

## Osa III: Systematisoitu Palautesilmukan Toteutus

Tämä osa esittelee full-stack-suunnitelman rakeiselle palautejärjestelmälle.

### 3.1 UI/UX-suunnittelu Rakeiselle Palautteelle

"Piilota"-toiminnon jälkeen käyttäjälle esitetään yhdellä klikkauksella toimivia vaihtoehtoja, jotka keräävät syyn hylkäämiselle:
- **"Ei relevantti"**: Aihe on täysin epäkiinnostava.
- **"Kiinnostava, mutta ei nyt"**: Aihe on relevantti, mutta ajankohta väärä.
- **"Liian pinnallinen / perusteet"**: Aihe oikea, syvyystaso väärä.
- **"Liian edistynyt / niche"**: Edellisen vastakohta.

### 3.2 API-suunnittelu Palautteen Välittämiseen

Palaute lähetetään standardoidulla RESTful API -rajapinnalla.

| Ominaisuus | Määrittely |
| :--- | :--- |
| **HTTP-metodi** | `POST` |
| **Rajapintapiste** | `/api/v1/feedback` |
| **Kuvaus** | Lähettää luokitellun käyttäjäpalautteen tietystä sisällöstä. |
| **Pyynnön runko** | `{ "content_id": "uuid", "user_id": "uuid", "feedback_type": "enum" }` |
| **`feedback_type` Enum** | `NOT_RELEVANT`, `NOT_NOW`, `TOO_SUPERFICIAL`, `TOO_ADVANCED` |
| **Onnistunut vastaus** | `202 Accepted` |
| **Virhevastaus** | `400 Bad Request`, `404 Not Found`, `422 Unprocessable Entity` |

### 3.3 Taustajärjestelmän Toteutus: Asynkroninen Käsittely

Jotta vältetään API-vastausajan hidastuminen, palautetapahtumat käsitellään asynkronisesti viestijonon (esim. RabbitMQ, Redis Pub/Sub) kautta.
1.  **API-vastaanotto:** `/api/v1/feedback` vastaanottaa pyynnön, validoi sen ja lähettää sen välittömästi viestijonoon.
2.  **Worker-palvelu:** Taustalla toimiva worker-palvelu kuuntelee jonoa, poimii tapahtumia ja suorittaa raskaan laskennan (vektoripäivitykset).

### 3.4 Kehittyneet Palautekäsittelijät

Eri palautetyypit käynnistävät erilaisia vektoripäivitysstrategioita, jotka hyödyntävät vektoriprojektiota.

- **`TOO_SUPERFICIAL`**: Vähentää käyttäjän profiilista sisällön yleistä, prototyyppistä osaa.
- **`TOO_ADVANCED`**: Vähentää käyttäjän profiilista sisällön spesifistä, syvällistä osaa.

**Koodiesimerkki: Palautetapahtuman Käsittely**
```python
def project_vector(v_to_project, v_target):
    """Laskee vektorin v_to_project projektion vektorille v_target."""
    return np.dot(v_to_project, v_target) / np.dot(v_target, v_target) * v_target

def get_topic_prototype_vector(content_id: str) -> np.ndarray:
    """Hakee tai laskee aiheen yleisen prototyyppivektorin (placeholder)."""
    prototype = np.array([0.5, 0.5, 0.1, 0.1, 0.1])
    return prototype / np.linalg.norm(prototype)

def process_feedback_event(feedback_event: dict):
    """
Käsittelee viestijonosta tulevan palautetapahtuman.
    """
    feedback_type = feedback_event["feedback_type"]
    user_vec = get_user_vector_from_db(feedback_event["user_id"])
    content_vec = get_content_vector_from_db(feedback_event["content_id"])
    
    W_STRONG = 0.15
    W_NUANCED = 0.08
    new_user_vec = None

    if feedback_type == "NOT_RELEVANT":
        new_user_vec = update_and_normalize_vector(user_vec, content_vec, -W_STRONG)
    
    elif feedback_type == "TOO_SUPERFICIAL":
        topic_prototype_vec = get_topic_prototype_vector(feedback_event["content_id"])
        general_component = project_vector(content_vec, topic_prototype_vec)
        new_user_vec = update_and_normalize_vector(user_vec, general_component, -W_NUANCED)

    elif feedback_type == "TOO_ADVANCED":
        topic_prototype_vec = get_topic_prototype_vector(feedback_event["content_id"])
        general_component = project_vector(content_vec, topic_prototype_vec)
        specific_component = content_vec - general_component
        new_user_vec = update_and_normalize_vector(user_vec, specific_component, -W_NUANCED)

    if new_user_vec is not None:
        save_user_vector_to_db(feedback_event["user_id"], new_user_vec)
```